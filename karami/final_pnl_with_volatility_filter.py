import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("💰 بک‌تست نهایی: بهترین ۲٪ کندل‌ها + فیلتر نوسان (ATR)")
print("=" * 70)

# 1. بارگذاری داده
def load_data():
    for p in ['data_EURUSD_1m.csv', '../forex_alpha/data_EURUSD_1m.csv']:
        try:
            df = pd.read_csv(p)
            for c in df.columns:
                if str(c).lower() == 'close':
                    return df[c].values
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
tf_60 = pd.Series(price).rolling(60).mean().bfill().values
coherence = 1.0 / (1.0 + np.abs(tf_5 - tf_15) + np.abs(tf_15 - tf_60))
entropy = shannon_entropy(returns)
vertex_score = (1 - np.clip(entropy / np.log2(10), 0, 1)) * np.abs(ent_corr) * coherence

hour_of_day = np.arange(n) % 1440 / 60.0
session_overlap = (((hour_of_day >= 8) & (hour_of_day <= 16)) & ((hour_of_day >= 13) & (hour_of_day <= 21))).astype(float)

high_20 = pd.Series(price).rolling(20).max().bfill().values
low_20 = pd.Series(price).rolling(20).min().bfill().values
dist_high = (high_20 - price) / (price + 1e-9)
dist_low = (price - low_20) / (price + 1e-9)

# 🚀 ویژگی جدید: ATR (میانگین دامنه نوسان)
tr = np.maximum(high_20 - low_20, np.maximum(np.abs(high_20 - price), np.abs(low_20 - price)))
atr = pd.Series(tr).rolling(14).mean().bfill().values
atr_ratio = atr / (price + 1e-9) # نوسان نسبی

momentum = pd.Series(price).diff(5).fillna(0).values
y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Entropy', 'Vertex', 'Coherence', 'Overlap', 'DistHigh', 'DistLow', 'ATR_Ratio']
X = np.column_stack([buyer, seller, ent_corr, momentum, entropy, vertex_score, coherence, session_overlap, dist_high, dist_low, atr_ratio])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, vertex_score, atr_ratio, price = X[valid], y_dir[valid], vertex_score[valid], atr_ratio[valid], price[valid]
n = len(X)

# 3. آموزش
split = int(n * 0.7)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
vx_te = vertex_score[split:]
atr_te = atr_ratio[split:]
price_te = price[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("\n⏳ آموزش مدل...")
np.random.seed(42); random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=50, pop_size=350, max_nodes=15)

if tree is None: sys.exit()

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
signals = np.sign(pred_te)
actual = np.sign(y_te)
mask_valid = actual != 0

# 4. انتخاب بهترین ۲٪ و اعمال فیلتر نوسان
threshold = np.percentile(vx_te, 98)
mask_vertex = (vx_te >= threshold) & mask_valid

# 🌟 فیلتر جدید: فقط زمانی که ATR از ۵ برابر اسپرد بیشتر است
spread = 0.0001
atr_threshold = spread * 5
mask_volatility = atr_te > atr_threshold

mask_final = mask_vertex & mask_volatility

print(f"\n📊 سیگنال‌های راس (بهترین ۲٪): {mask_vertex.sum()}")
print(f"📊 سیگنال‌های با نوسان کافی (ATR > 5*spread): {mask_final.sum()}")

# 5. شبیه‌سازی معاملات
initial_balance = 1000
balance = initial_balance
leverage = 10
trades = 0
win_trades = 0

for i in range(1, len(X_te)):
    if mask_final[i]:
        direction = signals[i]
        actual_move = (price_te[i] - price_te[i-1]) / price_te[i-1]
        net_move = (direction * actual_move) - spread
        
        if net_move > 0:
            win_trades += 1
            
        pnl = net_move * balance * leverage
        balance += pnl
        trades += 1

print("\n" + "=" * 70)
print("📊 نتایج بک‌تست نهایی (با فیلتر نوسان):")
print(f"  موجودی اولیه: ${initial_balance}")
print(f"  تعداد معاملات: {trades}")
if trades > 0:
    print(f"  تعداد معاملات برنده: {win_trades}")
    print(f"  موجودی نهایی: ${balance:.2f}")
    print(f"  سود/زیان خالص: {((balance - initial_balance) / initial_balance * 100):.2f}%")
else:
    print("  ⚠️ هیچ سیگنالی از فیلترها عبور نکرد.")
print("=" * 70)
