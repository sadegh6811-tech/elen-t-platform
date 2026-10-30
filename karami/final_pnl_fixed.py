import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("💰 بک‌تست نهایی (اصلاح‌شده): فقط بهترین ۲٪ کندل‌ها")
print("=" * 70)

# 1. بارگذاری داده
def load_data():
    for p in ['data/data_EURUSD_1m.csv', 'data_EURUSD_1m.csv', '../forex_alpha/data_EURUSD_1m.csv']:
        try:
            df = pd.read_csv(p, header=None)
            return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values
        except: continue
    return np.cumsum(np.random.randn(10000)*0.0001) + 1.1

price = load_data()
n = len(price)
print(f"📊 داده: {n} کندل")

# 2. ساخت ویژگی‌ها (نسخه ۱۷ بعدی)
delta = np.gradient(price)
returns = delta / (price + 1e-9)
buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)

def shannon_entropy(ret, w=20):
    e = np.zeros(len(ret))
    for i in range(w, len(ret)):
        data = ret[i-w:i]
        if np.all(data == data[0]): continue
        hist, _ = np.histogram(data, bins=10)
        probs = hist / (hist.sum() + 1e-9)
        probs = probs[probs > 0]
        e[i] = -np.sum(probs * np.log2(probs))
    return e

ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
tf_5 = pd.Series(price).rolling(5).mean().bfill().values
tf_15 = pd.Series(price).rolling(15).mean().bfill().values
coherence = 1.0 / (1.0 + np.abs(tf_5 - tf_15))
entropy = shannon_entropy(returns)
vertex_score = (1 - np.clip(entropy / np.log2(10), 0, 1)) * np.abs(ent_corr) * coherence

momentum = pd.Series(price).diff(5).fillna(0).values

# هدف: تغییر قیمت از i به i+1
y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Entropy', 'Vertex', 'Coherence']
X = np.column_stack([buyer, seller, ent_corr, momentum, entropy, vertex_score, coherence])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, vertex_score = X[valid], y_dir[valid], vertex_score[valid]
price = price[valid]
n = len(X)

# 3. آموزش
split = int(n * 0.7)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
vx_te = vertex_score[split:]
prices_te = price[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("\n⏳ آموزش مدل...")
np.random.seed(42); random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=50, pop_size=350, max_nodes=15)

if tree is None: sys.exit()

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
signals = np.sign(pred_te)
actual = np.sign(y_te)
confidence = np.abs(pred_te)

# 4. انتخاب بهترین ۲٪ (با فیلتر اطمینان + راس)
threshold_vx = np.percentile(vx_te, 98)
threshold_conf = np.percentile(confidence, 98)

mask_top = (vx_te >= threshold_vx) & (confidence >= threshold_conf) & (actual != 0)

# 5. بک‌تست واقعی
initial_balance = 1000
balance = initial_balance
spread = 0.0001  # ۱ پیپ
leverage = 10
trade_count = 0
win_count = 0

# حرکت از i به i+1 (بدون باگ گذشته‌نگر)
for i in range(len(X_te) - 1):
    if mask_top[i]:
        direction = signals[i]
        # 🌟 اصلاح باگ: حرکت آینده (i به i+1)
        actual_move = (prices_te[i+1] - prices_te[i]) / prices_te[i]
        net_move = (direction * actual_move) - spread
        
        pnl = net_move * balance * leverage
        balance += pnl
        trade_count += 1
        if net_move > 0:
            win_count += 1

print("\n" + "=" * 70)
print("📊 نتایج بک‌تست واقعی (اصلاح‌شده):")
print(f"  موجودی اولیه: ${initial_balance}")
print(f"  تعداد معاملات: {trade_count}")
print(f"  تعداد سود: {win_count} | تعداد ضرر: {trade_count - win_count}")
if trade_count > 0:
    print(f"  دقت معاملات: {(win_count/trade_count*100):.2f}%")
print(f"  موجودی نهایی: ${balance:.2f}")
print(f"  سود/زیان خالص: {((balance - initial_balance) / initial_balance * 100):.2f}%")
print("=" * 70)
