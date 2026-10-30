import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🔥 ترکیب نهایی: آشکارساز رأس + فیلتر اطمینان")
print("=" * 70)

# 1. بارگذاری داده
df = pd.read_csv('data/data_EURUSD_1m.csv', header=None)
price = pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

# 2. ساخت ویژگی‌ها
delta = np.gradient(price)
buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)

def rolling_corr(x, y, w=14):
    return pd.Series(x).rolling(w).corr(pd.Series(y)).fillna(0).values

ent_corr = rolling_corr(buyer, seller)
momentum = pd.Series(price).diff(5).fillna(0).values

def shannon_entropy(returns, window=20):
    entropy = np.zeros(len(returns))
    for i in range(window, len(returns)):
        hist, _ = np.histogram(returns[i-window:i], bins=8)
        probs = hist / (hist.sum() + 1e-9)
        probs = probs[probs > 0]
        entropy[i] = -np.sum(probs * np.log2(probs))
    return entropy

returns = delta / (price + 1e-9)
entropy = shannon_entropy(returns)
norm_entropy = np.clip(entropy / np.log2(8), 0, 1)

tf_5 = pd.Series(price).rolling(5).mean().bfill().values
tf_15 = pd.Series(price).rolling(15).mean().bfill().values
coherence = np.where(((tf_5 > tf_15) | (tf_5 < tf_15)), 1.0, 0.3) # ساده‌شده

vertex_score = (1 - norm_entropy) * np.abs(ent_corr) * coherence

y_dir = np.zeros(len(price))
y_dir[:-1] = np.sign(price[1:] - price[:-1])

features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Entropy', 'Vertex', 'Coherence']
X = np.column_stack([buyer, seller, ent_corr, momentum, entropy, vertex_score, coherence])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, vertex_score, price = X[valid][100:], y_dir[valid][100:], vertex_score[valid][100:], price[valid][100:]

split = int(len(X) * 0.7)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
vx_te = vertex_score[split:]
prices_te = price[split:]

# 3. آموزش
y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("⏳ آموزش مدل...")
np.random.seed(42)
random.seed(42)
tree, mse, a = gp_core_v27(X_tr, y_norm, features, generations=40, pop_size=300, max_nodes=12)

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
signals = np.sign(pred_te)
actual = np.sign(y_te)
confidence = np.abs(pred_te)

# 4. فیلتر ترکیبی: راس + اطمینان
print("\n" + "=" * 70)
print("🎯 نتایج فیلتر ترکیبی (راس + اطمینان)")
print("=" * 70)

# آزمایش ترکیب آستانه‌های مختلف
for vx_thresh in [0.0, 0.1, 0.2]:
    for conf_thresh in [0.0, 0.5, 1.0, 1.5, 2.0]:
        mask = (vx_te > vx_thresh) & (confidence > conf_thresh) & (actual != 0)
        num = mask.sum()
        if num < 5: continue
        
        acc = np.mean(signals[mask] == actual[mask]) * 100
        
        # محاسبه سود/زیان فرضی (هر سود = ۱ پیپ، هر ضرر = -۱ پیپ)
        trade_pnls = signals[mask] * actual[mask]  # 1 for win, -1 for loss
        total_pnl = trade_pnls.sum()
        
        star = "🏆" if acc > 90 else "✅" if acc > 80 else "⚠️"
        print(f"  {star} Vx>{vx_thresh:.1f}, Conf>{conf_thresh:.1f} | سیگنال: {num:4d} | دقت: {acc:5.2f}% | سود خالص: {total_pnl:+4d} پیپ")

print("\n" + "=" * 70)
