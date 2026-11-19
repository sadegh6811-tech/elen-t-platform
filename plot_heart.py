import numpy as np
import matplotlib.pyplot as plt

# تنظیمات فرمول
k = 35.21
x = np.linspace(-np.sqrt(3) + 0.01, np.sqrt(3) - 0.01, 1000)
x_abs = np.abs(x)

# محاسبه y (معادله تصویر)
y = - (x_abs ** (2/3)) + 0.9 * np.sin(k * x) * np.sqrt(3 - x**2)

# رسم نمودار
plt.figure(figsize=(6, 6))
plt.plot(x, y, color='crimson', linewidth=1.5)
plt.title('Mathematical Heart (ELEN-T Test)', fontsize=14)
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)
plt.axis('equal') # برای اینکه قلب کشیده نشود
plt.show()
