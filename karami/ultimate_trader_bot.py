import numpy as np
import pandas as pd
import random
import sys
import time
import warnings
import sympy as sp
import os
warnings.filterwarnings('ignore')

sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
try:
    from engine_v27_clean import gp_core_v27, evaluate_tree_safe, tree_to_sympy
except ImportError:
    print("❌ خطا: فایل موتور (engine_v27_clean.py) در پوشه sadegh پیدا نشد.")
    sys.exit(1)

print("🤖 ربات تریدر نهایی (Ultimate Trader Bot - 16D Entanglement Model)")
print("=" * 70)

# 1. بارگذاری هوشمند داده‌ها
def load_price_data():
    files_to_try = ["data_EURUSD_1m.csv", "../forex_alpha/data_EURUSD_1m.csv"]
    for f in files_to_try:
        if os.path.exists(f):
            try:
                # تلاش اول: خواندن با هدر
                df = pd.read_csv(f)
                cols = [str(c).lower() for c in df.columns]
                if 'close' in cols:
                    col_name = df.columns[cols.index('close')]
                    print(f"✅ داده‌های واقعی از {f} بارگذاری شد (ستون: {col_name}).")
                    return df[col_name].values
                else:
                    # تلاش دوم: خواندن بدون هدر (فرض فرمت OHLCV)
                    df_no_header = pd.read_csv(f, header=None)
                    if df_no_header.shape[1] >= 5:
                        print(f"✅ داده‌های واقعی (بدون هدر) از {f} بارگذاری شد (ستون ۴ به عنوان Close).")
                        return pd.to_numeric(df_no_header.iloc[:, 4], errors='coerce').dropna().values
            except Exception as e:
                print(f"⚠️ خطا در خواندن {f}: {e}")
                
    print("⚠️ داده واقعی پیدا نشد یا معتبر نبود. از داده شبیه‌سازی (Random Walk) استفاده می‌شود.")
    return np.cumsum(np.random.randn(10000)*0.0001) + 1.1

price = load_price_data()
n = len(price)
print(f"[*] تعداد کل کندل‌ها: {n}")

# 2. ساخت ویژگی‌های درهم‌تنیدگی
delta = np.gradient(price)
buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)

def rolling_corr(x, y, w=14):
    return pd.Series(x).rolling(w).corr(pd.Series(y)).bfill()

ent_corr = rolling_corr(buyer, seller)
quant_dist = np.abs(buyer - seller) / (buyer + seller + 1e-9)

tf_5m = pd.Series(price).rolling(5).mean().bfill()
tf_15m = pd.Series(price).rolling(15).mean().bfill()
tf_1h = pd.Series(price).rolling(60).mean().bfill()
tf_4h = pd.Series(price).rolling(240).mean().bfill()

state_bull = (tf_5m > tf_15m).astype(float)
state_bear = (tf_5m < tf_15m).astype(float)

y_direction = np.zeros(n)
y_direction[:-1] = np.sign(price[1:] - price[:-1])

features = ['Buyer', 'Seller', 'Ent', 'Dist', 'TF5', 'TF15', 'TF1h', 'TF4h', 'Bull', 'Bear', 'Momentum']
X = np.column_stack([buyer, seller, ent_corr, quant_dist, tf_5m, tf_15m, tf_1h, tf_4h, state_bull, state_bear, delta])

valid = np.isfinite(y_direction) & np.all(np.isfinite(X), axis=1)
X, y_direction, price = X[valid][100:], y_direction[valid][100:], price[valid][100:]
n = len(X)

y_m, y_s = y_direction.mean(), y_direction.std() + 1e-9
y_norm = (y_direction - y_m) / y_s

split = int(n * 0.8)
X_tr, y_tr = X[:split], y_norm[:split]
X_val, y_val = X[split:], y_norm[split:]

# 3. آموزش
print("\n[*] آموزش ربات با روش Boosting (کشف قانون درهم‌تنیدگی)...")
y_residual = np.copy(y_tr)
found_trees = []

for stage in range(3):
    print(f"  🔄 مرحله {stage+1} از ۳...")
    np.random.seed(42 + stage)
    random.seed(42 + stage)
    tree, mse, a = gp_core_v27(X_tr, y_residual, features, generations=30, pop_size=200, max_nodes=12)
    if tree is None: 
        print(f"    ⚠️ مرحله {stage+1} نتوانست مدلی بسازد.")
        break
    pred_tr = evaluate_tree_safe(tree, X_tr, features)
    pred_tr = np.nan_to_num(pred_tr)
    y_residual = y_residual - (a * pred_tr)
    found_trees.append((tree, a))

# 4. پیش‌بینی و ارزیابی
def predict(X_data):
    total = np.zeros(len(X_data))
    for tree, a in found_trees:
        p = evaluate_tree_safe(tree, X_data, features)
        p = np.nan_to_num(p)
        total += a * p
    return total

if len(found_trees) > 0:
    train_pred = np.sign(predict(X_tr))
    val_pred = np.sign(predict(X_val))

    train_acc = np.mean(train_pred == np.sign(y_tr)) * 100
    val_acc = np.mean(val_pred == np.sign(y_val)) * 100

    print("\n" + "=" * 70)
    print("📊 نتایج ارزیابی مدل:")
    print(f"  ✅ دقت روی داده‌های آموزش (Train):     {train_acc:.2f}%")
    print(f"  📉 دقت روی داده‌های تست (Validation):  {val_acc:.2f}%")

    # 5. بک‌تست با فیلتر اطمینان
    print("\n[*] بک‌تست با فیلتر اطمینان...")
    val_raw_pred = predict(X_val)
    confidence = np.abs(val_raw_pred)

    best_profit = 0
    best_threshold = 0
    best_trades = 0

    for threshold in [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        mask = confidence > threshold
        if mask.sum() < 10: continue
        
        signals = np.sign(val_raw_pred[mask])
        actual = np.sign(y_val[mask])
        acc_filtered = np.mean(signals == actual) * 100
        num_trades = mask.sum()
        
        print(f"  🎯 آستانه {threshold:.1f} | تعداد سیگنال: {num_trades} | دقت: {acc_filtered:.2f}%")
        
        if acc_filtered > best_profit:
            best_profit = acc_filtered
            best_threshold = threshold
            best_trades = num_trades

    print(f"\n🏆 بهترین آستانه: {best_threshold:.1f} با دقت {best_profit:.2f}% (روی {best_trades} معامله)")

    print("\n📜 فرمول‌های ربات:")
    for i, (tree, a) in enumerate(found_trees):
        try:
            expr = a * tree_to_sympy(tree)
            print(f"  مرحله {i+1}: {sp.expand(expr)}")
        except: pass

    print("\n" + "=" * 70)
else:
    print("\n❌ ربات نتوانست هیچ مدلی بسازد.")

print("=" * 70)
