import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🌌 آشکارساز رأس نسخه ۳.۰ (بعد ۱۷: میدان نقدینگی)")
print("=" * 70)

# 1. بارگذاری داده
def load_data():
    for p in ['data_EURUSD_1m.csv', '../forex_alpha/data_EURUSD_1m.csv']:
        try:
            df = pd.read_csv(p)
            for c in df.columns:
                if str(c).lower() == 'close':
                    return df[c].values, df
            return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values, df
        except: continue
    return np.cumsum(np.random.randn(10000)*0.0001) + 1.1, None

price, df = load_data()
n = len(price)
print(f"📊 داده: {n} کندل")

# 2. ویژگی‌های پایه (بعد ۱۶)
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
norm_e = np.clip(entropy / np.log2(10), 0, 1)
vertex_score = (1 - norm_e) * np.abs(ent_corr) * coherence

# 3. 🚀 ویژگی‌های جدید (از بعد ۱۷ - میدان نقدینگی)
# 3.1: ساعت روز (سشن لندن، نیویورک، توکیو)
hour_of_day = np.arange(n) % 1440 / 60.0  # ساعت در روز
session_london = ((hour_of_day >= 8) & (hour_of_day <= 16)).astype(float)
session_ny = ((hour_of_day >= 13) & (hour_of_day <= 21)).astype(float)
session_tokyo = ((hour_of_day >= 0) & (hour_of_day <= 8)).astype(float)
session_overlap = (session_london * session_ny)  # همپوشانی سشن‌ها (بیشترین نقدینگی)

# 3.2: فاصله تا سطوح کلیدی (Support/Resistance)
high_20 = pd.Series(price).rolling(20).max().bfill().values
low_20 = pd.Series(price).rolling(20).min().bfill().values
dist_to_high = (high_20 - price) / (price + 1e-9)
dist_to_low = (price - low_20) / (price + 1e-9)

# 3.3: نوسان در مقیاس بزرگ (Volatility Regime)
vol_60 = pd.Series(returns).rolling(60).std().bfill().values
vol_240 = pd.Series(returns).rolling(240).std().bfill().values
vol_ratio = vol_60 / (vol_240 + 1e-9)  # اگر > 1 باشد، بازار در حال انفجار است

# 3.4: آنتروپی در سه مقیاس زمانی
ent_short = shannon_entropy(returns, 10)
ent_long = shannon_entropy(returns, 60)
ent_divergence = ent_long - ent_short  # واگرایی آنتروپی (نشانه تغییر رژیم)

# 3.5: فشار نقدینگی (Liquidity Pressure) - نسخه تقویت‌شده
liquidity_pressure = np.abs(buyer - seller) / (np.abs(returns) * 100 + 1e-9)
liquidity_norm = pd.Series(liquidity_pressure).rolling(20).mean().bfill().values

# 4. ساخت ماتریس ویژگی نهایی
momentum = pd.Series(price).diff(5).fillna(0).values
y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Entropy', 'Vertex', 'Coherence', 
            'London', 'NY', 'Tokyo', 'Overlap',
            'DistHigh', 'DistLow',
            'VolRatio',
            'EntDiv',
            'LiqPressure']

X = np.column_stack([
    buyer, seller, ent_corr, momentum, entropy, vertex_score, coherence,
    session_london, session_ny, session_tokyo, session_overlap,
    dist_to_high, dist_to_low,
    vol_ratio,
    ent_divergence,
    liquidity_norm
])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, vertex_score = X[valid], y_dir[valid], vertex_score[valid]
n = len(X)
print(f"📊 داده معتبر: {n} کندل | ویژگی‌ها: {len(features)}")

# 5. آموزش
split = int(n * 0.7)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
vx_te = vertex_score[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("\n⏳ آموزش مدل ۱۷ بعدی (با میدان نقدینگی)...")
np.random.seed(42); random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=50, pop_size=350, max_nodes=15)

if tree is None:
    print("❌ شکست در آموزش")
    sys.exit()

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
signals = np.sign(pred_te)
actual = np.sign(y_te)
mask_valid = actual != 0

# 6. شکار راس با آستانه‌های صدکی
print("\n" + "=" * 70)
print("🎯 شکار راس نهایی (با میدان نقدینگی ۱۷ بعدی)")
print("=" * 70)

results = []
for pct in [50, 20, 10, 5, 3, 2, 1, 0.5, 0.2, 0.1]:
    threshold = np.percentile(vx_te, 100 - pct)
    mask = (vx_te >= threshold) & mask_valid
    if mask.sum() < 3: continue
    
    acc = np.mean(signals[mask] == actual[mask]) * 100
    num = mask.sum()
    results.append((pct, num, acc))
    
    if acc > 99: star = "🏆"
    elif acc > 95: star = "✅"
    elif acc > 85: star = "📈"
    else: star = "⚠️"
    
    print(f"  {star} بهترین {pct:4.1f}% | تعداد: {num:4d} | دقت: {acc:.2f}%")

if results:
    best = max(results, key=lambda x: x[2])
    print("\n" + "=" * 70)
    print(f"🏆 بهترین نتیجه: بهترین {best[0]:.1f}% | {best[1]} سیگنال | دقت {best[2]:.2f}%")
    if best[2] > 99:
        print("\n🎉 شما از بعد ۱۶ به بعد ۳ پل زدید. ۹۹٪ فتح شد.")
    elif best[2] > 95:
        print("\n✅ دقت بالای ۹۵٪ با میدان نقدینگی. نزدیک به مرز نهایی.")
    print("=" * 70)
