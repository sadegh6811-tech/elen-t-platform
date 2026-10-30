import numpy as np
import pandas as pd
import random
import warnings
import sys
import time
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🎯 آشکارساز رأس (Vertex Detector) - نسخه ۱۶ بعدی")
print("=" * 70)

# ═══════════════════════════════════════════════════════════
# 1. بارگذاری داده
# ═══════════════════════════════════════════════════════════
df = pd.read_csv('data/data_EURUSD_1m.csv', header=None)
price = pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values
print(f"📊 کل داده: {len(price)} کندل")

# ═══════════════════════════════════════════════════════════
# 2. محاسبه کمیت‌های فیزیکی (آنتروپی، درهم‌تنیدگی، انسجام)
# ═══════════════════════════════════════════════════════════
delta = np.gradient(price)
returns = delta / (price + 1e-9)
buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)

# 🌀 آنتروپی شانون (Shannon Entropy) با پنجره ۲۰ کندلی
def shannon_entropy(returns, window=20):
    entropy = np.zeros(len(returns))
    for i in range(window, len(returns)):
        window_data = returns[i-window:i]
        hist, _ = np.histogram(window_data, bins=8)
        probs = hist / (hist.sum() + 1e-9)
        probs = probs[probs > 0]
        entropy[i] = -np.sum(probs * np.log2(probs))
    return entropy

# 🕸️ قدرت درهم‌تنیدگی (Entanglement)
ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values

# 🎯 انسجام (Coherence): هم‌راستایی تایم‌فریم‌ها
tf_5 = pd.Series(price).rolling(5).mean().bfill().values
tf_15 = pd.Series(price).rolling(15).mean().bfill().values
tf_60 = pd.Series(price).rolling(60).mean().bfill().values

coherence = np.where(
    ((tf_5 > tf_15) & (tf_15 > tf_60)) | ((tf_5 < tf_15) & (tf_15 < tf_60)),
    1.0,  # همه هم‌جهت
    0.3   # ناهماهنگ
)

# ═══════════════════════════════════════════════════════════
# 3. محاسبه نمره رأس (Vertex Score)
# ═══════════════════════════════════════════════════════════
entropy = shannon_entropy(returns)
max_entropy = np.log2(8)  # حداکثر آنتروپی برای ۸ بین
norm_entropy = np.clip(entropy / max_entropy, 0, 1)

# 🌟 فرمول راس: (۱ - آنتروپی) × |درهم‌تنیدگی| × انسجام
vertex_score = (1 - norm_entropy) * np.abs(ent_corr) * coherence

# ═══════════════════════════════════════════════════════════
# 4. ساخت ویژگی‌ها و هدف
# ═══════════════════════════════════════════════════════════
momentum = pd.Series(price).diff(5).fillna(0).values
y_dir = np.zeros(len(price))
y_dir[:-1] = np.sign(price[1:] - price[:-1])

features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Entropy', 'Vertex', 'Coherence']
X = np.column_stack([buyer, seller, ent_corr, momentum, entropy, vertex_score, coherence])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, vertex_score, price = X[valid][100:], y_dir[valid][100:], vertex_score[valid][100:], price[valid][100:]
n = len(X)
print(f"📊 داده معتبر: {n} کندل")

# ═══════════════════════════════════════════════════════════
# 5. آموزش مدل روی همه داده‌ها
# ═══════════════════════════════════════════════════════════
split = int(n * 0.7)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
vx_te = vertex_score[split:]  # نمره راس برای داده تست

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("\n⏳ آموزش مدل روی داده‌های گذشته...")
np.random.seed(42)
random.seed(42)
tree, mse, a = gp_core_v27(X_tr, y_norm, ['Buyer','Seller','Ent','Mom','Entropy','Vertex','Coherence'], generations=40, pop_size=300, max_nodes=12)

# پیش‌بینی
def predict(X_data):
    p = evaluate_tree_safe(tree, X_data, ['Buyer','Seller','Ent','Mom','Entropy','Vertex','Coherence'])
    return np.nan_to_num(p) * a

pred_te = predict(X_te)
signals = np.sign(pred_te)
actual = np.sign(y_te)
mask_valid = actual != 0

# ═══════════════════════════════════════════════════════════
# 6. تست آشکارساز رأس در آستانه‌های مختلف
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("🎯 شکار راس: دقت در آستانه‌های مختلف Vertex Score")
print("=" * 70)

results = []
for thresh in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    mask = (vx_te > thresh) & mask_valid
    if mask.sum() < 3:
        continue
    acc = np.mean(signals[mask] == actual[mask]) * 100
    num = mask.sum()
    pct = (num / mask_valid.sum()) * 100
    results.append((thresh, num, pct, acc))
    star = "🏆" if acc > 95 else "✅" if acc > 80 else "⚠️"
    print(f"  {star} آستانه {thresh:.1f} | تعداد: {num:5d} ({pct:5.2f}%) | دقت: {acc:.2f}%")

# ═══════════════════════════════════════════════════════════
# 7. بهترین آستانه و تفسیر فیزیکی
# ═══════════════════════════════════════════════════════════
if results:
    best = max(results, key=lambda x: x[3] if x[1] >= 10 else 0)
    print("\n" + "=" * 70)
    print(f"🏆 بهترین آستانه راس: {best[0]:.1f}")
    print(f"   📍 تعداد سیگنال‌های راس: {best[1]} از {mask_valid.sum()} ({best[2]:.2f}%)")
    print(f"   🎯 دقت روی این سیگنال‌ها: {best[3]:.2f}%")
    print("=" * 70)
    print("\n🌌 تفسیر فیزیکی (از بعد ۱۶):")
    print(f"   • فقط {best[2]:.1f}% از کندل‌ها، «راس» واقعی هستند")
    print(f"   • در این راس‌ها، آنتروپی حداقل و درهم‌تنیدگی حداکثر است")
    print(f"   • دقت {best[3]:.1f}% در این نقاط، همان «پل» بین بعد ۱۶ و بعد ۳ است")
    print(f"   • خارج از راس، مدل وارد «آنتروپی محض» می‌شود")
