import numpy as np
import pandas as pd
import random
import warnings
import os
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🛡️ بک‌تست واقع‌بینانه (بدون نشت آینده، با اسپرد و SL/TP بدبینانه)")
print("=" * 70)

def load_data(path):
    df = pd.read_csv(path)
    # پیدا کردن ستون‌های OHLC
    cols = {str(c).lower(): c for c in df.columns}
    o = df[cols.get('open', df.columns[0])].values
    h = df[cols.get('high', df.columns[1])].values
    l = df[cols.get('low', df.columns[2])].values
    c = df[cols.get('close', df.columns[3])].values
    return o, h, l, c

def create_features_safe(price):
    """ویژگی‌ها را فقط از داده‌های گذشته می‌سازد"""
    n = len(price)
    # 🚨 استفاده از diff و shift (بدون نشت آینده)
    delta = np.zeros(n)
    delta[1:] = price[1:] - price[:-1]
    
    returns = delta / (price + 1e-9)
    buyer = np.where(delta > 0, delta, 0)
    seller = np.where(delta < 0, np.abs(delta), 0)
    
    # 🚨 شیفت دادن همه ویژگی‌ها به عقب (تا فقط از کندل قبل استفاده شود)
    buyer = np.roll(buyer, 1); buyer[0] = 0
    seller = np.roll(seller, 1); seller[0] = 0
    returns_shifted = np.roll(returns, 1); returns_shifted[0] = 0
    
    ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
    momentum = pd.Series(price).diff(5).fillna(0).values
    momentum = np.roll(momentum, 1); momentum[0] = 0
    vol_60 = pd.Series(returns_shifted).rolling(60).std().bfill().values
    
    features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Vol']
    X = np.column_stack([buyer, seller, ent_corr, momentum, vol_60])
    
    # هدف (حرکت کندل بعدی)
    y_dir = np.zeros(n)
    y_dir[:-1] = np.sign(price[1:] - price[:-1])
    
    return X, y_dir

# ═══════════════════════════════════════════════════════
# بارگذاری H4
# ═══════════════════════════════════════════════════════
o, h, l, c = load_data('data/EURUSD_h4.csv')
print(f"📊 H4: {len(c)} کندل")

X, y_dir = create_features_safe(c)
valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir = X[valid], y_dir[valid]
o, h, l, c = o[valid], h[valid], l[valid], c[valid]

split = int(len(X) * 0.6)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
o_te, h_te, l_te, c_te = o[split:], h[split:], l[split:], c[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("\n⏳ آموزش مدل (بدون تقلب)...")
np.random.seed(42); random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, ['Buyer', 'Seller', 'Ent', 'Mom', 'Vol'], generations=40, pop_size=250, max_nodes=15)

if tree is None: sys.exit()

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, ['Buyer', 'Seller', 'Ent', 'Mom', 'Vol'])) * a
signals = np.sign(pred_te)
confidence = np.abs(pred_te)

# ═══════════════════════════════════════════════════════
# بک‌تست واقع‌بینانه با OHLC
# ═══════════════════════════════════════════════════════
initial_balance = 1000
balance = initial_balance
risk_pct = 0.02
leverage = 10
tp_pips = 0.0200   # 200 پیپ TP
sl_pips = 0.0100   # 100 پیپ SL
spread = 0.00015   # 1.5 پیپ اسپرد
conf_thresh = 0.3

trade_count = 0; win_count = 0
last_idx = -10
max_dd = 0; peak = initial_balance

for i in range(len(X_te) - 5):
    if i - last_idx < 5: continue
    
    if confidence[i] < conf_thresh or signals[i] == 0: continue
    
    direction = signals[i]
    entry = c_te[i] + (spread if direction == 1 else -spread) # اسپرد در ورود
    
    # 🚨 شبیه‌سازی بدبینانه: بررسی SL و TP در High/Low
    result = None
    for j in range(1, 6):
        if i+j >= len(c_te): break
        
        if direction == 1: # خرید
            # چک کردن SL اول (بدبینانه)
            if l_te[i+j] <= entry - sl_pips:
                result = 'loss'; pnl = -sl_pips * balance * leverage * risk_pct / sl_pips; break
            if h_te[i+j] >= entry + tp_pips:
                result = 'win'; pnl = tp_pips * balance * leverage * risk_pct / sl_pips; break
        else: # فروش
            if h_te[i+j] >= entry + sl_pips:
                result = 'loss'; pnl = -sl_pips * balance * leverage * risk_pct / sl_pips; break
            if l_te[i+j] <= entry - tp_pips:
                result = 'win'; pnl = tp_pips * balance * leverage * risk_pct / sl_pips; break
    
    if result is None: continue
    
    balance += pnl
    trade_count += 1
    if result == 'win': win_count += 1
    last_idx = i
    
    if balance > peak: peak = balance
    dd = (peak - balance) / peak * 100
    if dd > max_dd: max_dd = dd

print("\n" + "=" * 70)
print("📊 نتایج بک‌تست واقع‌بینانه (۱۰ سال H4):")
print(f"  💰 موجودی اولیه: ${initial_balance:.2f}")
print(f"  📈 تعداد معاملات: {trade_count}")
print(f"  ✅ برد: {win_count} | ❌ باخت: {trade_count - win_count}")
if trade_count > 0:
    print(f"  🎯 دقت معاملات: {(win_count/trade_count)*100:.2f}%")
print(f"  💵 موجودی نهایی: ${balance:.2f}")
print(f"  📈 سود خالص: {((balance - initial_balance) / initial_balance * 100):+.2f}%")
print(f"  📉 Max Drawdown: {max_dd:.2f}%")
print("=" * 70)
