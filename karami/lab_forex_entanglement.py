import numpy as np
import pandas as pd
import random
import sys
import time
import warnings
import sympy as sp
warnings.filterwarnings('ignore')

# استفاده از موتور v27 (چون در پوشه sadegh است، مسیر مطلق می‌دهیم)
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe, tree_to_sympy

print("🌌 آزمایشگاه درهم‌تنیدگی کوانتومی بازار (ER=EPR)")
print("=" * 75)

# 1. بارگذاری داده‌ها
file_path = "data_EURUSD_1m.csv"
try:
    df = pd.read_csv(file_path)
    price = df['Close'].values
    volume = df['Volume'].values if 'Volume' in df.columns else np.random.uniform(100, 1000, len(price))
    print(f"✅ داده‌های واقعی از {file_path} بارگذاری شد.")
except:
    print(f"⚠️ فایل {file_path} در این پوشه پیدا نشد. از داده شبیه‌سازی استفاده می‌شود.")
    price = np.random.uniform(1.0, 1.2, 5000)
    volume = np.random.uniform(100, 1000, 5000)

n = len(price)

# 2. استخراج حالت‌های ذره‌ای
delta_price = np.gradient(price)
buyer_power = np.where(delta_price > 0, delta_price * volume, 0)
seller_power = np.where(delta_price < 0, np.abs(delta_price) * volume, 0)

# 3. ساخت سنسور درهم‌تنیدگی
def rolling_correlation(x, y, window=14):
    # 🛠️ اصلاح باگ پانداس جدید
    return pd.Series(x).rolling(window).corr(pd.Series(y)).bfill()

entanglement_corr = rolling_correlation(buyer_power, seller_power)
quantum_distance = np.abs(buyer_power - seller_power) / (buyer_power + seller_power + 1e-9)

# 4. تایم‌فریم‌ها و حالت‌های بازار
tf_1m = pd.Series(price).rolling(1).mean().bfill()
tf_5m = pd.Series(price).rolling(5).mean().bfill()
tf_15m = pd.Series(price).rolling(15).mean().bfill()
tf_30m = pd.Series(price).rolling(30).mean().bfill()
tf_1h = pd.Series(price).rolling(60).mean().bfill()
tf_4h = pd.Series(price).rolling(240).mean().bfill()
tf_1d = pd.Series(price).rolling(1440).mean().bfill()

state_bull = (tf_5m > tf_15m).astype(float)
state_bear = (tf_5m < tf_15m).astype(float)
state_range = 1 - (state_bull + state_bear)

# 5. تعریف سه مدل (۹، ۱۱، ۱۶)
features_9d = ['Buyer', 'Seller', 'Ent_Corr', 'Liq', 'Noise', 'TF_1m', 'TF_15m', 'TF_1h', 'State_Bull']
X_9d = np.column_stack([buyer_power, seller_power, entanglement_corr, np.abs(delta_price), np.abs(price - tf_15m), tf_1m, tf_15m, tf_1h, state_bull])

features_11d = ['Buyer', 'Seller', 'Ent_Corr', 'Quant_Dist', 'Liq', 'Noise', 'TF_1m', 'TF_5m', 'TF_15m', 'TF_4h', 'State_Bull']
X_11d = np.column_stack([buyer_power, seller_power, entanglement_corr, quantum_distance, np.abs(delta_price), np.abs(price - tf_15m), tf_1m, tf_5m, tf_15m, tf_4h, state_bull])

features_16d = ['Buyer', 'Seller', 'Ent_Corr', 'Quant_Dist', 'Liq', 'Noise', 'TF_1m', 'TF_5m', 'TF_15m', 'TF_30m', 'TF_1h', 'TF_4h', 'TF_1d', 'Bull', 'Bear', 'Range']
X_16d = np.column_stack([buyer_power, seller_power, entanglement_corr, quantum_distance, np.abs(delta_price), np.abs(price - tf_15m), tf_1m, tf_5m, tf_15m, tf_30m, tf_1h, tf_4h, tf_1d, state_bull, state_bear, state_range])

# هدف
y = np.zeros(n)
y[:-1] = (price[1:] - price[:-1]) / (price[:-1] + 1e-9)
y = y * 10000 

# پاکسازی
valid = np.isfinite(y) & np.all(np.isfinite(X_16d), axis=1)
y = y[valid]
X_9d = X_9d[valid][100:]
X_11d = X_11d[valid][100:]
X_16d = X_16d[valid][100:]
y = y[100:]

y_m, y_s = y.mean(), y.std() + 1e-9
y_norm = (y - y_m) / y_s
split = int(len(y) * 0.8)

def run_experiment(name, X, features):
    print(f"\n🔬 در حال تست مدل {name} (با درهم‌تنیدگی)...")
    X_tr, y_tr = X[:split], y_norm[:split]
    X_val, y_val = X[split:], y_norm[split:]
    
    np.random.seed(42)
    random.seed(42)
    start = time.time()
    
    tree, mse, a = gp_core_v27(X_tr, y_tr, features, generations=40, pop_size=300, max_nodes=15)
    
    if tree is not None:
        pred_val_norm = evaluate_tree_safe(tree, X_val, features)
        pred_val_norm = np.nan_to_num(pred_val_norm, nan=0.0)
        pred_val_raw = (a * pred_val_norm) * y_s + y_m
        y_val_raw = y_val * y_s + y_m
        
        r2_val = 1 - np.sum((y_val_raw - pred_val_raw)**2) / np.sum((y_val_raw - np.mean(y_val_raw))**2)
        
        print(f"  🏆 دقت R²: {r2_val:.4f} | زمان: {time.time() - start:.1f} ثانیه")
        try:
            final_expr = a * tree_to_sympy(tree)
            final_expr = final_expr * sp.Float(y_s) + sp.Float(y_m)
            print(f"  📜 فرمول حرکت: {sp.expand(final_expr)}")
        except: pass
        return r2_val
    return -1

r2_9 = run_experiment("۹ بعدی (Entanglement Basic)", X_9d, features_9d)
r2_11 = run_experiment("۱۱ بعدی (Entanglement M-Theory)", X_11d, features_11d)
r2_16 = run_experiment("۱۶ بعدی (Entanglement Hypercube)", X_16d, features_16d)

print("\n" + "=" * 75)
print("📊 خلاصه نتایج (کشف قانون درهم‌تنیدگی):")
print(f"  مدل ۹ بعدی:  R² = {r2_9:.4f}")
print(f"  مدل ۱۱ بعدی: R² = {r2_11:.4f}")
print(f"  مدل ۱۶ بعدی: R² = {r2_16:.4f}")
print("=" * 75)
