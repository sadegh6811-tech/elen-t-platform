import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("🌌 افزودن بعد هفتم: همبستگی بین بازارها")
print("=" * 70)

# فرض: داده‌های DXY و طلا را دارید (یا از یک API می‌گیرید)
# برای نمونه، از داده‌های شبیه‌سازی شده استفاده می‌کنیم
df = pd.read_csv('data/data_EURUSD_1m.csv', header=None)
price = pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

# در دنیای واقعی، این‌ها را از یک API واقعی می‌گیرید
np.random.seed(42)
dxy = price * (1 + np.random.randn(len(price)) * 0.0001)  # شبیه‌سازی DXY
gold = price * (1 + np.random.randn(len(price)) * 0.0002) # شبیه‌سازی طلا

# همبستگی غلتان
def rolling_corr(x, y, w=20):
    return pd.Series(x).rolling(w).corr(pd.Series(y)).fillna(0).values

corr_dxy = rolling_corr(price, dxy)
corr_gold = rolling_corr(price, gold)

# همبستگی متقابل
cross_market_strength = (np.abs(corr_dxy) + np.abs(corr_gold)) / 2

print(f"✅ داده‌های بعد هفتم ساخته شد: {len(cross_market_strength)} کندل")
print(f"📊 میانگین قدرت همبستگی: {np.mean(cross_market_strength):.4f}")
print(f"📊 حداکثر قدرت همبستگی: {np.max(cross_market_strength):.4f}")
print("\n💡 این ویژگی جدید را به X اضافه کنید تا مدل بعد ۷ را ببیند.")
