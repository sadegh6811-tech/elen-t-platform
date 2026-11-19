import numpy as np
import pandas as pd

# تعداد نمونه‌ها
n_samples = 1000

# دامنه x (باید بین -sqrt(3) و +sqrt(3) باشد)
x = np.linspace(-np.sqrt(3) + 0.01, np.sqrt(3) - 0.01, n_samples)

# ثابت فرمول
k = 35.21

# محاسبه y (با استفاده از توان کسری به روش امن برای اعداد منفی)
# توجه: x^(2/3) معادل (x^2)^(1/3) است
x_abs = np.abs(x)
y_classic = (x_abs ** (2/3)) * np.sign(x) * -1  # برای اینکه نوک قلب پایین باشد
# فرمول اصلی در تصویر: y = x^(2/3) + 0.9 sin(kx) * sqrt(3 - x^2)
# اما در تصویر، قلب برعکس است (نوک پایین). پس علامت توان را اصلاح می‌کنیم:
y = - (x_abs ** (2/3)) + 0.9 * np.sin(k * x) * np.sqrt(3 - x**2)

# اضافه کردن کمی نویز (مثل داده‌های واقعی)
y_noisy = y + np.random.normal(0, 0.05, n_samples)

# ذخیره در CSV
df = pd.DataFrame({"x": x, "y": y_noisy})
df.to_csv("heart_formula.csv", index=False)

print(f"✅ دیتاست 'heart_formula.csv' با {n_samples} نمونه ساخته شد.")
print("   این فایل را می‌توانید به موتور ELEN-T بدهید تا فرمول را کشف کند.")
