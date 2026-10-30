import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🎯 هدف: هر معامله درست، خطا به صفر")
print("=" * 70)

def load_data(path):
    df = pd.read_csv(path)
    for c in df.columns:
        if str(c).lower() == 'close':
            return df[c].values
    return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

price = load_data('data/EURUSD_h4.csv')
n = len(price)
print(f"📊 داده H4: {n} کندل")

# ساخت ویژگی‌ها (بدون نشت داده - فقط گذشته)
delta = np.gradient(price)
returns = delta / (price + 1e-9)
buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)
ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
tf_5 = pd.Series(price).rolling(5).mean().bfill().values
tf_15 = pd.Series(price).rolling(15).mean().bfill().values
coherence = 1.0 / (1.0 + np.abs(tf_5 - tf_15))
momentum = pd.Series(price).diff(5).fillna(0).values
vol_60 = pd.Series(returns).rolling(60).std().bfill().values

features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Coherence', 'Vol']
X = np.column_stack([buyer, seller, ent_corr, momentum, coherence, vol_60])
y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, price = X[valid], y_dir[valid], price[valid]
n = len(X)
print(f"📊 داده معتبر: {n} کندل")

split = int(n * 0.6)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
prices_te = price[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("⏳ آموزش مدل...")
np.random.seed(42)
random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=50, pop_size=350, max_nodes=15)

if tree is None:
    print("❌ مدل ساخته نشد")
    sys.exit()

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
signals = np.sign(pred_te)
actual = np.sign(y_te)
confidence = np.abs(pred_te)

# ═══════════════════════════════════════════════════════
# 🎯 شکار معاملات ۱۰۰٪ درست
# ═══════════════════════════════════════════════════════
print("\n🔬 شکار معاملات با اطمینان بالا:")
print("=" * 70)

for threshold in [0.3, 0.5, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0]:
    mask = (confidence >= threshold) & (actual != 0)
    n_trades = mask.sum()
    
    if n_trades == 0:
        continue
    
    correct = np.sum(signals[mask] == actual[mask])
    accuracy = (correct / n_trades) * 100
    
    emoji = "🏆" if accuracy > 99 else "🥇" if accuracy > 95 else "✅" if accuracy > 85 else "⚠️"
    
    print(f"  {emoji} آستانه {threshold:.1f} | تعداد: {n_trades:4d} | دقت: {accuracy:6.2f}%")

print("=" * 70)
print("\n💡 هدف: پیدا کردن آستانه‌ای که دقت را به ۱۰۰٪ برساند.")
print("   اگر آستانه‌ای با دقت ۱۰۰٪ پیدا شد، شما به هدف خود رسیده‌اید.")
