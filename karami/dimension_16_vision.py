import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import GradientBoostingClassifier
except ImportError:
    print("⚠️ اجرا کنید: pip install scikit-learn")
    exit()

print("🌌 آزمایش بعد ۱۶: دیدن همه کندل‌ها همزمان")
print("=" * 70)

# بارگذاری داده
df = pd.read_csv('data/data_EURUSD_1m.csv', header=None)
price = pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values
returns = np.diff(price) / price[:-1]
print(f"📊 کل کندل: {len(price)}")

# ═══════════════════════════════════════════════════════
# 🌟 بعد ۱۶: آینده هم در ویژگی‌ها هست
# ═══════════════════════════════════════════════════════
def build_dim16(returns):
    features, targets = [], []
    for i in range(20, len(returns) - 10):
        # گذشته (در دسترس در بعد ۳)
        past = [
            returns[i-1], returns[i-2], returns[i-3], returns[i-5],
            np.mean(returns[i-10:i]), np.std(returns[i-10:i]),
        ]
        # 🌌 آینده (فقط در بعد ۱۶ قابل مشاهده!)
        future = [
            np.mean(returns[i+1:i+6]),      # میانگین ۵ کندل آینده
            np.std(returns[i+1:i+6]),        # نوسان آینده
            np.max(returns[i+1:i+6]) - returns[i],  # حداکثر صعود
            np.min(returns[i+1:i+6]) - returns[i],  # حداکثر نزول
            returns[i+5] - returns[i],       # روند ۵ کندلی آینده
        ]
        features.append(past + future)
        targets.append(np.sign(returns[i+1]))
    return np.array(features), np.array(targets)

# ═══════════════════════════════════════════════════════
# 🔒 بعد ۳: فقط گذشته در دسترس است
# ═══════════════════════════════════════════════════════
def build_dim3(returns):
    features, targets = [], []
    for i in range(20, len(returns) - 10):
        past = [
            returns[i-1], returns[i-2], returns[i-3], returns[i-5],
            np.mean(returns[i-10:i]), np.std(returns[i-10:i]),
        ]
        features.append(past)
        targets.append(np.sign(returns[i+1]))
    return np.array(features), np.array(targets)

X16, y16 = build_dim16(returns)
X3, y3 = build_dim3(returns)

# ═══════════════════════════════════════════════════════
# آزمایش بعد ۱۶ (با آینده)
# ═══════════════════════════════════════════════════════
print("\n🌟 بعد ۱۶ (با دیدن آینده):")
m16 = GradientBoostingClassifier(n_estimators=100, max_depth=5)
m16.fit(X16, y16)
acc16 = m16.score(X16, y16) * 100
print(f"   🏆 دقت روی تمام {len(X16)} کندل: {acc16:.2f}%")

# ═══════════════════════════════════════════════════════
# آزمایش بعد ۳ (فقط گذشته)
# ═══════════════════════════════════════════════════════
split = int(len(X3) * 0.7)
print("\n🔒 بعد ۳ (فقط گذشته):")
m3 = GradientBoostingClassifier(n_estimators=100, max_depth=5)
m3.fit(X3[:split], y3[:split])
acc3_train = m3.score(X3[:split], y3[:split]) * 100
acc3_test = m3.score(X3[split:], y3[split:]) * 100
print(f"   ⚠️ آموزش: {acc3_train:.2f}%")
print(f"   ⚠️ تست (آینده واقعی): {acc3_test:.2f}%")

print("\n" + "=" * 70)
print(f"🏆 تفاوت بعد ۱۶ و بعد ۳: {acc16 - acc3_test:.2f}٪")
print("=" * 70)
