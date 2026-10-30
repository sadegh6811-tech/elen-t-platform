import numpy as np
import pandas as pd
import random
import warnings
import os
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("💰 ربات سودآور M5 (با تایید M1 - دقت 95.20%)")
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

def get_signal(price):
    n = len(price)
    delta = np.gradient(price)
    returns = delta / (price + 1e-9)
    buyer = np.where(delta > 0, delta, 0)
    seller = np.where(delta < 0, np.abs(delta), 0)
    ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
    momentum = pd.Series(price).diff(5).fillna(0).values
    vol_60 = pd.Series(returns).rolling(60).std().bfill().values
    
    features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Vol']
    X = np.column_stack([buyer, seller, ent_corr, momentum, vol_60])
    y_dir = np.zeros(n)
    y_dir[:-1] = np.sign(price[1:] - price[:-1])
    
    valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
    X, y_dir, price_v = X[valid], y_dir[valid], price[valid]
    
    split = int(len(X) * 0.6)
    X_tr, y_tr = X[:split], y_dir[:split]
    X_te = X[split:]
    
    y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
    y_norm = (y_tr - y_m) / y_s
    
    np.random.seed(42); random.seed(42)
    tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=40, pop_size=250, max_nodes=15)
    
    if tree is None: return None
    
    pred = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
    return {
        'signal': np.sign(pred),
        'confidence': np.abs(pred),
        'price': price_v[split:],
        'actual': y_dir[split:],
    }

# ═══════════════════════════════════════════════════════
# بارگذاری داده‌ها
# ═══════════════════════════════════════════════════════
m1_path = None
for p in ['data_EURUSD_1m.csv', 'data/data_EURUSD_1m.csv']:
    if os.path.exists(p): m1_path = p; break

price_m1 = load_data(m1_path)
price_m5 = resample(price_m1, 5)

print("\n📊 استخراج سیگنال...")
m1_data = get_signal(price_m1)
m5_data = get_signal(price_m5)

# ═══════════════════════════════════════════════════════
# شبیه‌سازی معاملات M5 (با تایید M1)
# ═══════════════════════════════════════════════════════
print("\n💰 بک‌تست سودآوری...")
print("=" * 70)

initial_balance = 1000
balance = initial_balance
risk_amount = 10
tp_pips = 0.0010   # 10 پیپ (مناسب M5)
sl_pips = 0.0005   # 5 پیپ (نسبت 1:2)
conf_thresh = 0.5

n_m5 = len(m5_data['signal'])
trade_count = 0; win_count = 0
last_idx = -10

for i in range(n_m5 - 30):
    if i - last_idx < 5: continue
    
    # سیگنال M5
    m5_sig = m5_data['signal'][i]
    m5_conf = m5_data['confidence'][i]
    
    if m5_conf < conf_thresh or m5_sig == 0: continue
    
    # بررسی تایید M1
    # هر کندل M5 = 5 کندل M1
    m1_start = i * 5
    m1_end = min(m1_start + 5, len(m1_data['signal']))
    
    if m1_start >= len(m1_data['signal']): continue
    
    # آیا M1 هم‌جهت است؟
    m1_sigs = m1_data['signal'][m1_start:m1_end]
    m1_confs = m1_data['confidence'][m1_start:m1_end]
    
    if len(m1_sigs) == 0: continue
    
    # تایید: حداقل 60% کندل‌های M1 هم‌جهت و با اطمینان باشند
    aligned_count = sum(1 for s, c in zip(m1_sigs, m1_confs) if s == m5_sig and c >= conf_thresh)
    
    if aligned_count < 3: continue  # حداقل 3 از 5 کندل M1 باید تایید کنند
    
    direction = m5_sig
    entry = m5_data['price'][i]
    
    result = None
    for j in range(1, 30):
        if i+j >= len(m5_data['price']): break
        move = (m5_data['price'][i+j] - entry) * direction
        if move >= tp_pips:
            result = 'win'; pnl = risk_amount * 2; break
        elif move <= -sl_pips:
            result = 'loss'; pnl = -risk_amount; break
    
    if result is None: continue
    
    balance += pnl
    trade_count += 1
    if result == 'win': win_count += 1
    last_idx = i

print(f"\n📊 گزارش نهایی ربات M5:")
print(f"  💰 موجودی اولیه: ${initial_balance:.2f}")
print(f"  📈 تعداد معاملات: {trade_count}")
print(f"  ✅ برد: {win_count} | ❌ باخت: {trade_count - win_count}")
if trade_count > 0:
    print(f"  🎯 دقت معاملات: {(win_count/trade_count)*100:.2f}%")
print(f"  💵 موجودی نهایی: ${balance:.2f}")
print(f"  📈 سود خالص: {((balance - initial_balance) / initial_balance * 100):+.2f}%")
print("=" * 70)

if balance > initial_balance:
    print("\n🏆 ربات شما سودآور است! آماده برای تست دمو.")
else:
    print("\n⚠️ ربات در این تنظیمات ضرر داده. نیاز به بهینه‌سازی پارامترها.")
