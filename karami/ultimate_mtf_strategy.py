import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🚀 استراتژی نهایی چند تایم‌فریمی (ورود در راس ۱ دقیقه، معامله در ۵/۱۵ دقیقه)")
print("=" * 75)

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

# 2. ساخت ویژگی‌های ۱۷ بعدی (همان مدل برنده)
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

momentum = pd.Series(price).diff(5).fillna(0).values
y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Entropy', 'Vertex', 'Coherence']
X = np.column_stack([buyer, seller, ent_corr, momentum, entropy, vertex_score, coherence])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, vertex_score, price = X[valid], y_dir[valid], vertex_score[valid], price[valid]
n = len(X)

# 3. آموزش
split = int(n * 0.7)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
vx_te = vertex_score[split:]
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

# 4. انتخاب بهترین ۲٪ (نقاط ورود)
threshold = np.percentile(vx_te, 98)
mask_entry = (vx_te >= threshold) & mask_valid

print(f"\n📍 تعداد نقاط ورود (راس در ۱ دقیقه): {mask_entry.sum()}")

# 5. شبیه‌سازی معاملات با هولدینگ تایم‌های مختلف
initial_balance = 1000
spread = 0.0001
leverage = 10

holding_periods = [1, 5, 15, 30, 60] # ۱ دقیقه تا ۱ ساعت
results = []

for hold in holding_periods:
    balance = initial_balance
    trades = 0
    wins = 0
    
    for i in range(len(X_te) - hold):
        if mask_entry[i]:
            direction = signals[i]
            entry_price = price_te[i]
            exit_price = price_te[i + hold]
            
            # محاسبه سود بر اساس حرکت واقعی در طول هولدینگ تایم
            actual_move = (exit_price - entry_price) / entry_price
            net_move = (direction * actual_move) - spread
            
            if net_move > 0:
                wins += 1
            
            pnl = net_move * balance * leverage
            balance += pnl
            trades += 1
            
    profit_pct = (balance - initial_balance) / initial_balance * 100
    win_rate = (wins / trades * 100) if trades > 0 else 0
    results.append((hold, trades, win_rate, balance, profit_pct))

# 6. نمایش نتایج
print("\n" + "=" * 75)
print("📊 نتایج مقایسه هولدینگ تایم‌ها:")
print("=" * 75)
print(f"{'هولدینگ':<12} | {'تعداد':<6} | {'وین‌ریت':<8} | {'موجودی':<10} | {'سود/زیان':<10}")
print("-" * 75)

for hold, trades, win_rate, balance, profit in results:
    emoji = "🏆" if profit > 20 else "✅" if profit > 0 else "⚠️"
    print(f"{emoji} {hold:>3} دقیقه   | {trades:<6} | {win_rate:>6.2f}% | ${balance:>9.2f} | {profit:>+7.2f}%")

# پیدا کردن بهترین
best = max(results, key=lambda x: x[4])
print("\n" + "=" * 75)
print(f"🏆 بهترین استراتژی: هولدینگ {best[0]} دقیقه")
print(f"   • تعداد معاملات: {best[1]}")
print(f"   • وین‌ریت: {best[2]:.2f}%")
print(f"   • موجودی نهایی: ${best[3]:.2f}")
print(f"   • سود خالص: {best[4]:+.2f}%")
print("=" * 75)

if best[4] > 0:
    print("\n🎉 استراتژی شما سودآور است!")
    print("   بینش شما (ورود در ۱ دقیقه، خروج در تایم بالاتر) درست بود.")
else:
    print("\n⚠️ هنوز سودآور نیست. نیاز به فیلترهای بیشتر.")
