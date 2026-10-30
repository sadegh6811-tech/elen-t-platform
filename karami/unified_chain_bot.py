import numpy as np
import pandas as pd
import random
import warnings
import os
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🌌 ربات زنجیره واحد (Unified Chain)")
print("=" * 70)

def load_data(path):
    df = pd.read_csv(path)
    for c in df.columns:
        if str(c).lower() == 'close':
            return df[c].values
    return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

def resample(price_1m, minutes):
    n = len(price_1m) // minutes * minutes
    if n < minutes * 100: return np.array([])
    return price_1m[:n].reshape(-1, minutes)[:, -1]

def build_tf_features(price):
    """ساخت ۴ ویژگی برای هر تایم‌فریم"""
    delta = np.gradient(price)
    returns = delta / (price + 1e-9)
    buyer = np.where(delta > 0, delta, 0)
    seller = np.where(delta < 0, np.abs(delta), 0)
    ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
    momentum = pd.Series(price).diff(5).fillna(0).values
    return buyer, seller, ent_corr, momentum

# ═══════════════════════════════════════════════════════
# 🌟 زنجیره واحد: ۲۰ ویژگی از ۵ تایم‌فریم
# ═══════════════════════════════════════════════════════
def build_unified_chain(price_m1, price_m5, price_m15, price_h4, price_d1):
    """
    برای هر کندل M1، ویژگی‌های همه تایم‌فریم‌ها را می‌گیریم
    و به صورت یک زنجیره ۲۰تایی کنار هم می‌چینیم.
    """
    n = len(price_m1)
    
    # ویژگی‌های M1
    m1_b, m1_s, m1_e, m1_m = build_tf_features(price_m1)
    
    # ویژگی‌های M5, M15, H4, D1 (با Resample زمانی)
    def align_features(price_high, ratio):
        b, s, e, m = build_tf_features(price_high)
        aligned_b = np.zeros(n)
        aligned_s = np.zeros(n)
        aligned_e = np.zeros(n)
        aligned_m = np.zeros(n)
        for i in range(n):
            idx = min(i // ratio, len(b) - 1)
            if idx >= 0:
                aligned_b[i] = b[idx]
                aligned_s[i] = s[idx]
                aligned_e[i] = e[idx]
                aligned_m[i] = m[idx]
        return aligned_b, aligned_s, aligned_e, aligned_m
    
    m5_b, m5_s, m5_e, m5_m = align_features(price_m5, 5)
    m15_b, m15_s, m15_e, m15_m = align_features(price_m15, 15)
    h4_b, h4_s, h4_e, h4_m = align_features(price_h4, 240)
    d1_b, d1_s, d1_e, d1_m = align_features(price_d1, 1440)
    
    # 🌟 زنجیره ۲۰تایی
    X = np.column_stack([
        m1_b, m1_s, m1_e, m1_m,
        m5_b, m5_s, m5_e, m5_m,
        m15_b, m15_s, m15_e, m15_m,
        h4_b, h4_s, h4_e, h4_m,
        d1_b, d1_s, d1_e, d1_m,
    ])
    
    features = [
        'M1_Buyer', 'M1_Seller', 'M1_Ent', 'M1_Mom',
        'M5_Buyer', 'M5_Seller', 'M5_Ent', 'M5_Mom',
        'M15_Buyer', 'M15_Seller', 'M15_Ent', 'M15_Mom',
        'H4_Buyer', 'H4_Seller', 'H4_Ent', 'H4_Mom',
        'D1_Buyer', 'D1_Seller', 'D1_Ent', 'D1_Mom',
    ]
    
    return X, features, price_m1

# ═══════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════
m1_path = None
for p in ['data_EURUSD_1m.csv', 'data/data_EURUSD_1m.csv']:
    if os.path.exists(p): m1_path = p; break

price_m1 = load_data(m1_path)
price_m5 = resample(price_m1, 5)
price_m15 = resample(price_m1, 15)
price_h4 = load_data('data/EURUSD_h4.csv')
price_d1 = load_data('data/EURUSD_d1.csv')

print(f"\n📊 ساخت زنجیره واحد از ۵ تایم‌فریم...")
X, features, price = build_unified_chain(price_m1, price_m5, price_m15, price_h4, price_d1)
n = len(X)

y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, price = X[valid], y_dir[valid], price[valid]
n = len(X)
print(f"📊 زنجیره معتبر: {n} کندل × {X.shape[1]} ویژگی")

# آموزش
split = int(n * 0.6)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
prices_te = price[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("\n⏳ آموزش مدل روی زنجیره واحد...")
np.random.seed(42); random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=50, pop_size=350, max_nodes=20)

if tree is None:
    print("❌ مدل ساخته نشد"); sys.exit()

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
signals = np.sign(pred_te)
actual = np.sign(y_te)
confidence = np.abs(pred_te)
mask = actual != 0

print("\n📊 دقت زنجیره واحد در آستانه‌های مختلف:")
print("=" * 70)
print(f"{'آستانه':<12} | {'تعداد':<10} | {'دقت':<12}")
print("-" * 50)

for thresh in [0.0, 0.3, 0.5, 0.7, 1.0, 1.5]:
    m = (confidence >= thresh) & mask
    if m.sum() < 5: continue
    acc = np.mean(signals[m] == actual[m]) * 100
    emoji = "🏆" if acc > 99 else "🥇" if acc > 95 else "✅" if acc > 85 else "⚠️"
    print(f"{thresh:<12.1f} | {m.sum():<10} | {acc:<8.2f}% {emoji}")

print("=" * 70)
print(f"\n📜 فرمول کشف‌شده (بخشی):")
print(str(tree)[:200])
