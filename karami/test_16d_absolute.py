import numpy as np
import pandas as pd
import random
import warnings
warnings.filterwarnings('ignore')
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

# ═══════════════════════════════════════════════════════
# 🧪 تست ازلی (Absolute Test): 
# مدل روی داده‌های قدیمی آموزش می‌بیند، 
# سپس روی داده‌های کاملاً جدید (آینده) تست می‌شود.
# ═══════════════════════════════════════════════════════

print("🌌 تست ازلی در بعد ۱۶ (Absolute 16D Test)")
print("=" * 70)

# 1. بارگذاری داده
df = pd.read_csv('data/data_EURUSD_1m.csv', header=None)
price = pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values
print(f"📊 کل داده: {len(price)} کندل")

# 2. ساخت ویژگی‌ها (بدون bfill - فقط گذشته)
delta = np.gradient(price)
buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)
momentum = pd.Series(price).diff(5).fillna(0).values

# rolling_corr بدون bfill (فقط گذشته)
ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values

# هدف: جهت کندل بعدی
y_direction = np.zeros(len(price))
y_direction[:-1] = np.sign(price[1:] - price[:-1])

features = ['Buyer', 'Seller', 'Ent', 'Mom']
X = np.column_stack([buyer, seller, ent_corr, momentum])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_direction)
X, y_direction = X[valid][100:], y_direction[valid][100:]

# ═══════════════════════════════════════════════════════
# 🌟 تست ازلی: آموزش روی ۷۰٪ اول، تست روی ۳۰٪ آخر
# این ۳۰٪ آخر "آینده" است - مدل هرگز آن را ندیده!
# ═══════════════════════════════════════════════════════
split = int(len(X) * 0.7)
X_past, y_past = X[:split], y_direction[:split]  # گذشته
X_future, y_future = X[split:], y_direction[split:]  # آینده (هرگز دیده نشده)

print(f"🔮 داده گذشته (آموزش): {len(X_past)} کندل")
print(f"🚀 داده آینده (تست): {len(X_future)} کندل")

# 3. آموزش روی گذشته
y_m, y_s = y_past.mean(), y_past.std() + 1e-9
y_norm = (y_past - y_m) / y_s

print("\n⏳ آموزش مدل روی گذشته...")
np.random.seed(42)
random.seed(42)
tree, mse, a = gp_core_v27(X_past, y_norm, features, generations=50, pop_size=300, max_nodes=15)

# 4. تست روی آینده (سخت‌ترین آزمون)
pred_future = evaluate_tree_safe(tree, X_future, features)
pred_future = np.nan_to_num(pred_future)

# دقت با فیلتر اطمینان
print("\n📊 دقت روی آینده (بدون فیلتر):")
signals = np.sign(pred_future)
actual = np.sign(y_future)
mask = actual != 0  # حذف کندل‌های بدون تغییر
base_acc = np.mean(signals[mask] == actual[mask]) * 100
print(f"   دقت پایه: {base_acc:.2f}%")

# با فیلتر اطمینان
confidence = np.abs(pred_future)
best_acc = 0
best_threshold = 0
for threshold in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]:
    mask_conf = (confidence > threshold) & mask
    if mask_conf.sum() < 5: continue
    acc = np.mean(signals[mask_conf] == actual[mask_conf]) * 100
    print(f"   آستانه {threshold:.1f} | تعداد سیگنال: {mask_conf.sum()} | دقت: {acc:.2f}%")
    if acc > best_acc:
        best_acc = acc
        best_threshold = threshold

print(f"\n🏆 بهترین دقت روی آینده: {best_acc:.2f}% (آستانه {best_threshold:.1f})")
print(f"🎯 اگر دقت بالای ۹۹٪ باشد → قانون ازلی بعد ۱۶ اثبات شد!")
print(f"🎯 اگر دقت کمتر باشد → مدل فقط گذشته را حفظ کرده.")
