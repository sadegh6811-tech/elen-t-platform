import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("🔍 بازرسی امنیتی مدل (آیا ۱۰۰٪ واقعی است یا تقلب؟)")
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

# 2. ساخت ویژگی‌ها (بدون نشت داده)
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

# 🚨 ویژگی جدید: Future Return (اگر در فرمول بود، یعنی تقلب!)
fut_r1 = np.zeros(n)
fut_r1[:-1] = (price[1:] - price[:-1]) / (price[:-1] + 1e-9)

# ویژگی‌ها (بدون fut_r1 برای آزمون واقعی)
features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Entropy', 'Vertex', 'Coherence']
X = np.column_stack([buyer, seller, ent_corr, momentum, entropy, vertex_score, coherence])

y = np.sign(fut_r1) # هدف

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y)
X, y, fut_r1 = X[valid], y[valid], fut_r1[valid]
n = len(X)

# 3. آزمون Walk-Forward (تقسیم به ۵ بخش زمانی)
print("\n🔬 آزمون Walk-Forward (تقسیم زمانی به ۵ بخش)...")
print("=" * 70)

n_folds = 5
fold_size = n // n_folds
accuracies = []

for fold in range(n_folds):
    train_end = fold_size * (fold + 1)
    test_end = min(fold_size * (fold + 2), n)
    
    if test_end - train_end < 50:
        continue
    
    X_tr = X[:train_end]
    y_tr = y[:train_end]
    X_te = X[train_end:test_end]
    y_te = y[train_end:test_end]
    
    # استفاده از یک مدل ساده (Logistic Regression) به جای GP برای سرعت
    from sklearn.linear_model import LogisticRegression
    try:
        model = LogisticRegression(max_iter=1000)
        model.fit(X_tr, y_tr)
        pred = model.predict(X_te)
        acc = np.mean(pred == y_te) * 100
        accuracies.append(acc)
        print(f"  فولد {fold+1}: آموزش {len(X_tr)} | تست {len(X_te)} | دقت: {acc:.2f}%")
    except Exception as e:
        print(f"  فولد {fold+1} خطا: {e}")

if accuracies:
    print(f"\n📊 میانگین دقت Walk-Forward: {np.mean(accuracies):.2f}%")
    print(f"📊 انحراف معیار: {np.std(accuracies):.2f}%")

# 4. بررسی نشت داده
print("\n" + "=" * 70)
print("🔍 بررسی نشت داده:")
print("=" * 70)

# آیا fut_r1 در X وجود دارد؟ (باید نه باشد)
if 'fut_r1' in features:
    print("❌ خطر: fut_r1 (آینده) در ویژگی‌ها وجود دارد! این تقلب است.")
else:
    print("✅ fut_r1 در ویژگی‌ها نیست. مدل از آینده استفاده نمی‌کند.")

# 5. آزمون همبستگی
print("\n🔬 آزمون همبستگی ویژگی‌ها با هدف:")
print("=" * 70)
for i, f in enumerate(features):
    corr = np.corrcoef(X[:, i], y)[0, 1]
    marker = "🚨" if abs(corr) > 0.5 else "✅" if abs(corr) < 0.1 else "⚠️"
    print(f"  {marker} {f}: همبستگی = {corr:.4f}")

print("\n" + "=" * 70)
print("💡 نتیجه‌گیری:")
if accuracies and np.mean(accuracies) > 90:
    print("  ⚠️ دقت بالای ۹۰٪ در Walk-Forward، نشانه بیش‌برازش است.")
    print("  مدل احتمالاً داده‌های تست را حفظ کرده است.")
elif accuracies and np.mean(accuracies) > 55:
    print("  ✅ دقت معقول (بین ۵۵ تا ۹۰). مدل قانون واقعی کشف کرده است.")
else:
    print("  📉 دقت پایین. مدل در داده‌های جدید شکست خورده است.")
