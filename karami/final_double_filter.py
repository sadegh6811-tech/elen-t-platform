import numpy as np
import pandas as pd
import random
import warnings
import os
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🏆 فیلتر دوگانه: همدوسی + اطمینان (هدف: 99%)")
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

def get_raw(price):
    delta = np.gradient(price)
    b = np.where(delta > 0, delta, 0)
    s = np.where(delta < 0, np.abs(delta), 0)
    return b, s

# ═══════════════════════════════════════════════════════
# ساخت زنجیره با همدوسی
# ═══════════════════════════════════════════════════════
def build_chain(price_m1, price_m5, price_m15, price_h4, price_d1):
    n = len(price_m1)
    b_m1, s_m1 = get_raw(price_m1)
    b_m5, s_m5 = get_raw(price_m5)
    b_m15, s_m15 = get_raw(price_m15)
    b_h4, s_h4 = get_raw(price_h4)
    b_d1, s_d1 = get_raw(price_d1)
    
    def align(arr, ratio):
        out = np.zeros(n)
        for i in range(n):
            idx = min(i // ratio, len(arr) - 1)
            if idx >= 0: out[i] = arr[idx]
        return out
    
    b_m5_a = align(b_m5, 5); s_m5_a = align(s_m5, 5)
    b_m15_a = align(b_m15, 15); s_m15_a = align(s_m15, 15)
    b_h4_a = align(b_h4, 240); s_h4_a = align(s_h4, 240)
    b_d1_a = align(b_d1, 1440); s_d1_a = align(s_d1, 1440)
    
    coherence = np.zeros(n)
    for i in range(n):
        signs = []
        for b, s in [(b_m1[i], s_m1[i]), (b_m5_a[i], s_m5_a[i]), 
                     (b_m15_a[i], s_m15_a[i]), (b_h4_a[i], s_h4_a[i]), (b_d1_a[i], s_d1_a[i])]:
            if b > s: signs.append(1)
            elif b < s: signs.append(-1)
            else: signs.append(0)
        if all(x == 1 for x in signs): coherence[i] = 1.0
        elif all(x == -1 for x in signs): coherence[i] = -1.0
        else: coherence[i] = 0.0
    
    X = np.column_stack([b_m1, s_m1, b_m5_a, s_m5_a, b_m15_a, s_m15_a, b_h4_a, s_h4_a, b_d1_a, s_d1_a, coherence])
    features = ['M1_B', 'M1_S', 'M5_B', 'M5_S', 'M15_B', 'M15_S', 'H4_B', 'H4_S', 'D1_B', 'D1_S', 'Coherence']
    return X, features, coherence, price_m1

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

X, features, coherence, price = build_chain(price_m1, price_m5, price_m15, price_h4, price_d1)
n = len(X)

y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, price, coherence = X[valid], y_dir[valid], price[valid], coherence[valid]
n = len(X)

split = int(n * 0.6)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
coh_te = coherence[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("\n⏳ آموزش مدل...")
np.random.seed(42); random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=50, pop_size=350, max_nodes=20)

if tree is None: sys.exit()

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
signals = np.sign(pred_te)
actual = np.sign(y_te)
confidence = np.abs(pred_te)

# ═══════════════════════════════════════════════════════
# 🎯 فیلتر دوگانه
# ═══════════════════════════════════════════════════════
print("\n📊 فیلتر دوگانه (همدوسی + اطمینان):")
print("=" * 70)
print(f"{'آستانه اطمینان':<18} | {'تعداد':<10} | {'دقت':<10}")
print("-" * 50)

best_acc = 0
best_thresh = 0
best_n = 0

# فقط کندل‌هایی که همدوسی کامل دارند
mask_coh = (np.abs(coh_te) == 1.0) & (actual != 0)

for conf_thresh in [0.0, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 2.5, 3.0]:
    mask = mask_coh & (confidence >= conf_thresh)
    n_trades = mask.sum()
    if n_trades < 3: continue
    
    correct = np.sum(signals[mask] == actual[mask])
    acc = (correct / n_trades) * 100
    
    emoji = "🏆" if acc > 99 else "🥇" if acc > 95 else "✅" if acc > 85 else "⚠️"
    print(f"{conf_thresh:<18.1f} | {n_trades:<10} | {acc:<6.2f}% {emoji}")
    
    if acc > best_acc and n_trades >= 5:
        best_acc = acc
        best_thresh = conf_thresh
        best_n = n_trades

print("=" * 70)
print(f"\n🏆 بهترین نتیجه:")
print(f"   • آستانه اطمینان: {best_thresh}")
print(f"   • تعداد معاملات: {best_n}")
print(f"   • دقت: {best_acc:.2f}%")

if best_acc > 99:
    print("\n🎉 شما به هدف رسیدید! دقت بالای 99% در همدوسی کامل!")
else:
    print(f"\n⚠️ هنوز {100-best_acc:.2f}% باقی مانده. نیاز به داده‌های بنیادی داریم.")
