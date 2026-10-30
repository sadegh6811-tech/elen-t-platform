import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("🔬 آزمون نهایی: بدون نشت داده (Walk-Forward)")
print("=" * 70)

def load_data(path):
    df = pd.read_csv(path)
    for c in df.columns:
        if str(c).lower() == 'close':
            return df[c].values
    return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

print("\n📊 بارگذاری داده H4...")
price = load_data('data/EURUSD_h4.csv')
n = len(price)
print(f"📊 تعداد کندل‌ها: {n}")

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

fut_r = np.zeros(n)
fut_r[:-1] = np.sign(price[1:] - price[:-1])

# 🚨 ویژگی‌ها (بدون fut_r)
features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Entropy', 'Vertex', 'Coherence']
X = np.column_stack([buyer, seller, ent_corr, momentum, entropy, vertex_score, coherence])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(fut_r)
X, y = X[valid], fut_r[valid]
n = len(X)
print(f"📊 داده معتبر: {n} کندل")

def fit_linear(X, y):
    X_b = np.column_stack([X, np.ones(len(X))])
    try:
        return np.linalg.lstsq(X_b, y, rcond=None)[0]
    except:
        return np.zeros(X.shape[1] + 1)

def predict_linear(X, w):
    X_b = np.column_stack([X, np.ones(len(X))])
    return np.sign(X_b @ w)

print("\n🔬 آزمون Walk-Forward (با حذف نشت داده)...")
print("=" * 70)

n_folds = 5
fold_size = n // n_folds
accuracies = []

for fold in range(n_folds):
    train_end = fold_size * (fold + 1)
    test_end = min(fold_size * (fold + 2), n)
    
    if test_end - train_end < 50: continue
    
    X_tr, y_tr = X[:train_end], y[:train_end]
    X_te, y_te = X[train_end:test_end], y[train_end:test_end]
    
    w = fit_linear(X_tr, y_tr)
    pred = predict_linear(X_te, w)
    acc = np.mean(pred == y_te) * 100
    accuracies.append(acc)
    print(f"  فولد {fold+1}: آموزش {len(X_tr)} | تست {len(X_te)} | دقت: {acc:.2f}%")

if accuracies:
    mean_acc = np.mean(accuracies)
    std_acc = np.std(accuracies)
    print(f"\n📊 میانگین دقت Walk-Forward: {mean_acc:.2f}%")
    print(f"📊 انحراف معیار: {std_acc:.2f}%")
    
    print("\n" + "=" * 70)
    print("💡 نتیجه‌گیری نهایی:")
    if mean_acc > 90:
        print(f"  🚨 خطر: دقت {mean_acc:.2f}% در Walk-Forward، نشانه نشت داده یا Overfitting است.")
    elif mean_acc > 55:
        print(f"  ✅ دقت {mean_acc:.2f}% معقول است. مدل قانون واقعی کشف کرده (بدون تقلب).")
    else:
        print(f"  📉 دقت {mean_acc:.2f}% پایین است. مدل در داده‌های جدید شکست خورده.")

print("\n" + "=" * 70)
print("🔍 بررسی نهایی:")
print("=" * 70)
for i, f in enumerate(features):
    corr = np.corrcoef(X[:, i], y)[0, 1]
    marker = "🚨" if abs(corr) > 0.5 else "✅" if abs(corr) < 0.1 else "⚠️"
    print(f"  {marker} {f}: همبستگی با هدف = {corr:.4f}")
print("=" * 70)
