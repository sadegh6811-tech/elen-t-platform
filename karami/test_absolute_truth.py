import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("🔬 تست نهایی: آیا 100% روی 9 کندل واقعی است یا سراب؟")
print("=" * 70)

# بارگذاری داده
df = pd.read_csv('data/data_EURUSD_1m.csv', header=None)
price = pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

# ساخت ویژگی‌ها (بدون ویژگی‌های inf)
delta = np.gradient(price)
buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)

def rolling_corr(x, y, w=14):
    return pd.Series(x).rolling(w).corr(pd.Series(y)).fillna(0).values

ent_corr = rolling_corr(buyer, seller)
momentum = pd.Series(price).diff(5).fillna(0).values

y_dir = np.zeros(len(price))
y_dir[:-1] = np.sign(price[1:] - price[:-1])

# ═══════════════════════════════════════════════════════
# 🌟 بررسی 9 کندل برنده
# ═══════════════════════════════════════════════════════
# فرض: شما 9 کندل را در بخش Validation پیدا کرده‌اید
# اینجا نگاه می‌کنیم که آن کندل‌ها کجای تاریخ هستند

# ساخت X و y
X = np.column_stack([buyer, seller, ent_corr, momentum])
valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, price = X[valid][100:], y_dir[valid][100:], price[valid][100:]

split = int(len(X) * 0.7)
X_te = X[split:]
y_te = y_dir[split:]

# پیدا کردن کندل‌هایی که در آن‌ها بازار حرکت قوی داشته
strong_moves = np.abs(y_te) > 0
print(f"📊 تعداد کل کندل‌های تست: {len(y_te)}")
print(f"📊 تعداد کندل‌هایی که حرکت داشتند: {strong_moves.sum()}")

# توزیع حرکت‌های قوی
print("\n📊 توزیع حرکت‌ها در 9 کندل برنده:")
print(f"   • میانگین حرکت: {np.mean(y_te[strong_moves]):.4f}")
print(f"   • انحراف معیار حرکت: {np.std(y_te[strong_moves]):.4f}")

# شبیه‌سازی: اگر 9 کندل تصادفی انتخاب کنیم، چند بار 100% می‌شود؟
print("\n🎲 تست تصادفی (Monte Carlo):")
win_counts = []
for _ in range(1000):
    random_indices = np.random.choice(len(y_te), 9, replace=False)
    # فرض: مدل همیشه جهت را درست پیش‌بینی می‌کند
    wins = np.sum(np.sign(y_te[random_indices]) != 0)
    win_counts.append(wins)

print(f"   • میانگین برد در 9 انتخاب تصادفی: {np.mean(win_counts):.2f}")
print(f"   • احتمال اینکه 9 انتخاب تصادفی همگی حرکت داشته باشند: {np.mean([w == 9 for w in win_counts])*100:.2f}%")

print("\n💡 نتیجه:")
print("اگر احتمال Monte Carlo کمتر از 1% باشد، انتخاب شما واقعی است.")
print("اگر بیشتر از 1% باشد، احتمالاً یک تصادف آماری بوده است.")
