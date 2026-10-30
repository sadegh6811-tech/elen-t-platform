import numpy as np
import pandas as pd
import random
import sys
import warnings
import sympy as sp
warnings.filterwarnings('ignore')

sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe, tree_to_sympy

print("🌌 مدل کوانتومی ۱۶ بعدی (حداکثر دقت)")
print("=" * 70)

# 1. بارگذاری داده
try:
    df = pd.read_csv("data_EURUSD_1m.csv")
    price = df['Close'].values if 'Close' in df.columns else df.iloc[:, 4].values
except:
    try:
        df = pd.read_csv("../forex_alpha/data_EURUSD_1m.csv")
        price = df['Close'].values if 'Close' in df.columns else df.iloc[:, 4].values
    except:
        print("⚠️ داده پیدا نشد. شبیه‌سازی...")
        price = np.cumsum(np.random.randn(10000)*0.0001) + 1.1

n = len(price)
print(f"[*] تعداد کندل‌ها: {n}")

# 2. بازسازی فضای فاز ۱۶ بعدی (Takens' Theorem)
print("[*] بازسازی فضای فاز ۱۶ بعدی...")
embedding_dim = 16
tau = 2 # تاخیر زمانی
offset = (embedding_dim - 1) * tau
length_target = n - offset

X_phase = np.zeros((length_target, embedding_dim))
for i in range(embedding_dim):
    start = i * tau
    X_phase[:, i] = price[start:start + length_target]

# 3. ساخت ویژگی‌های اضافی
delta = np.gradient(price)
buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)
ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).bfill().values
quant_dist = np.abs(buyer - seller) / (buyer + seller + 1e-9)
tf_5m = pd.Series(price).rolling(5).mean().bfill().values
tf_15m = pd.Series(price).rolling(15).mean().bfill().values
tf_1h = pd.Series(price).rolling(60).mean().bfill().values
tf_4h = pd.Series(price).rolling(240).mean().bfill().values
state_bull = (tf_5m > tf_15m).astype(float)
state_bear = (tf_5m < tf_15m).astype(float)

# ویژگی‌های جدید
X_phase_mean = np.mean(X_phase, axis=0)
lorentzian_dist = np.log(1 + np.sum(np.abs(X_phase - X_phase_mean), axis=1))
quantum_momentum = np.gradient(X_phase[:, 0])

# 🛠️ باگ‌گیری: هم‌تراز کردن دقیق طول‌ها
price_aligned = price[offset:]
delta_aligned = delta[offset:]
buyer_aligned = buyer[offset:]
seller_aligned = seller[offset:]
ent_corr_aligned = ent_corr[offset:]
quant_dist_aligned = quant_dist[offset:]
tf_5m_aligned = tf_5m[offset:]
tf_15m_aligned = tf_15m[offset:]
tf_1h_aligned = tf_1h[offset:]
tf_4h_aligned = tf_4h[offset:]
bull_aligned = state_bull[offset:]
bear_aligned = state_bear[offset:]

# این دو از قبل هم‌طول X_phase هستند
lorentzian_aligned = lorentzian_dist
qmomentum_aligned = quantum_momentum

features = ['X_phase_1', 'X_phase_2', 'Buyer', 'Seller', 'Ent', 'Dist', 'TF5', 'TF15', 'TF1h', 'TF4h', 'Bull', 'Bear', 'Lorentz', 'Q_Momentum']

# ماتریس ویژگی‌ها
X = np.column_stack([
    X_phase[:, 0], 
    X_phase[:, 1], 
    buyer_aligned, seller_aligned, ent_corr_aligned, quant_dist_aligned,
    tf_5m_aligned, tf_15m_aligned, tf_1h_aligned, tf_4h_aligned,
    bull_aligned, bear_aligned, lorentzian_aligned, qmomentum_aligned
])

# هدف: جهت حرکت
y_direction = np.zeros(length_target)
y_direction[:-1] = np.sign(price_aligned[1:] - price_aligned[:-1])

valid = np.isfinite(y_direction) & np.all(np.isfinite(X), axis=1)
X, y_direction = X[valid], y_direction[valid]
n_valid = len(X)

y_m, y_s = y_direction.mean(), y_direction.std() + 1e-9
y_norm = (y_direction - y_m) / y_s

split = int(n_valid * 0.8)
X_tr, y_tr = X[:split], y_norm[:split]
X_val, y_val = X[split:], y_norm[split:]

# 4. آموزش با Boosting ۱۰ مرحله‌ای
print("\n[*] آموزش با Boosting ۱۰ مرحله‌ای (برای رسیدن به ۹۹٪)...")
y_residual = np.copy(y_tr)
found_trees = []

for stage in range(10):
    print(f"  🔄 مرحله {stage+1}/10...")
    np.random.seed(100 + stage)
    random.seed(100 + stage)
    tree, mse, a = gp_core_v27(X_tr, y_residual, features, generations=40, pop_size=250, max_nodes=12)
    if tree is None: break
    pred_tr = np.nan_to_num(evaluate_tree_safe(tree, X_tr, features))
    y_residual = y_residual - (a * pred_tr)
    found_trees.append((tree, a))

# 5. پیش‌بینی
def predict(X_data):
    total = np.zeros(len(X_data))
    for tree, a in found_trees:
        total += a * np.nan_to_num(evaluate_tree_safe(tree, X_data, features))
    return total

train_pred = np.sign(predict(X_tr))
val_pred = np.sign(predict(X_val))

train_acc = np.mean(train_pred == np.sign(y_tr)) * 100
val_acc = np.mean(val_pred == np.sign(y_val)) * 100

print("\n" + "=" * 70)
print("📊 نتایج:")
print(f"  ✅ دقت آموزش (Train):     {train_acc:.2f}%")
print(f"  📉 دقت تست (Validation):  {val_acc:.2f}%")

# 6. فیلتر اطمینان با آستانه‌های بسیار بالا
print("\n[*] بک‌تست با آستانه‌های بسیار سخت‌گیرانه...")
val_raw_pred = predict(X_val)
confidence = np.abs(val_raw_pred)

best_acc = 0
best_threshold = 0
best_trades = 0

for threshold in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]:
    mask = confidence > threshold
    if mask.sum() < 5: continue
    
    signals = np.sign(val_raw_pred[mask])
    actual = np.sign(y_val[mask])
    acc = np.mean(signals == actual) * 100
    num = mask.sum()
    
    print(f"  🎯 آستانه {threshold:.1f} | سیگنال: {num} | دقت: {acc:.2f}%")
    
    if acc > best_acc:
        best_acc = acc
        best_threshold = threshold
        best_trades = num

print(f"\n🏆 بهترین نتیجه: آستانه {best_threshold:.1f} با دقت {best_acc:.2f}% (روی {best_trades} سیگنال)")
print("=" * 70)

# 7. نمایش فرمول‌ها
print("\n📜 فرمول‌های ربات (ترکیب ۱۰ مرحله):")
for i, (tree, a) in enumerate(found_trees):
    try:
        expr = a * tree_to_sympy(tree)
        print(f"  مرحله {i+1}: {sp.expand(expr)}")
    except: pass
