import numpy as np
import pandas as pd
import random
import warnings
import os
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("💰 بک‌تست سیستم تایید سلسله‌مراتبی در H1 (نسخه اصلاح‌شده)")
print("=" * 70)

def load_data(path):
    df = pd.read_csv(path)
    for c in df.columns:
        if str(c).lower() == 'close':
            return df[c].values
    return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

def resample(price, minutes):
    n = len(price) // minutes * minutes
    if n < minutes * 10: return np.array([]) # کاهش آستانه به 10
    return price[:n].reshape(-1, minutes)[:, -1]

def get_signal(price, split_ratio=0.5):
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
    
    split_idx = int(len(X) * split_ratio)
    X_tr, y_tr = X[:split_idx], y_dir[:split_idx]
    X_te, y_te = X[split_idx:], y_dir[split_idx:]
    price_te = price_v[split_idx:]
    
    y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
    y_norm = (y_tr - y_m) / y_s
    
    np.random.seed(42); random.seed(42)
    tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=40, pop_size=250, max_nodes=15)
    
    if tree is None: return None
    
    pred = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
    return {
        'signal': np.sign(pred),
        'confidence': np.abs(pred),
        'actual': y_te,
        'price': price_te,
    }

# بارگذاری
m1_path = None
for p in ['data_EURUSD_1m.csv', 'data/data_EURUSD_1m.csv']:
    if os.path.exists(p): m1_path = p; break

price_m1 = load_data(m1_path)

# 🚀 افزایش طول تست به 6000 کندل (برای داشتن H1 کافی)
COMMON_TEST_LENGTH_M1 = 6000 
price_m1_common = price_m1[-COMMON_TEST_LENGTH_M1:]
price_m5_common = resample(price_m1, 5)[-COMMON_TEST_LENGTH_M1//5:]
price_m15_common = resample(price_m1, 15)[-COMMON_TEST_LENGTH_M1//15:]
price_h1_common = resample(price_m1, 60)[-COMMON_TEST_LENGTH_M1//60:]

print(f"📊 داده‌های تست: M1={len(price_m1_common)} | M5={len(price_m5_common)} | M15={len(price_m15_common)} | H1={len(price_h1_common)}")

# استخراج سیگنال‌ها با چک ایمنی
print("\n🔬 آموزش مدل‌ها...")
tf_signals = {}
for name, price in [('M1', price_m1_common), ('M5', price_m5_common), 
                     ('M15', price_m15_common), ('H1', price_h1_common)]:
    if len(price) < 20: 
        print(f"   ⚠️ {name} رد شد (داده کافی نیست: {len(price)})")
        continue
    print(f"   🔬 {name} ({len(price)} کندل)...")
    sig = get_signal(price, split_ratio=0.5)
    if sig: tf_signals[name] = sig

# 🛡️ لایه محافظتی: اگر H1 وجود نداشت، برنامه متوقف شود
if 'H1' not in tf_signals:
    print("\n❌ متاسفانه داده کافی برای H1 وجود ندارد. لطفاً طول داده را بیشتر کنید.")
    sys.exit()

# سیستم تایید سلسله‌مراتبی برای H1
print("\n🏛️ شناسایی سیگنال‌های H1 با تایید M1+M5+M15...")
CONF_THRESH = 0.3
h1_trades = []

for i in range(len(tf_signals['M1']['signal'])):
    m1_sig = tf_signals['M1']['signal'][i]
    if tf_signals['M1']['confidence'][i] < CONF_THRESH or m1_sig == 0: continue
    
    # M5
    if 'M5' not in tf_signals: continue
    idx_m5 = min(i // 5, len(tf_signals['M5']['signal']) - 1)
    if tf_signals['M5']['confidence'][idx_m5] < CONF_THRESH or tf_signals['M5']['signal'][idx_m5] != m1_sig: continue
    
    # M15
    if 'M15' not in tf_signals: continue
    idx_m15 = min(i // 15, len(tf_signals['M15']['signal']) - 1)
    if tf_signals['M15']['confidence'][idx_m15] < CONF_THRESH or tf_signals['M15']['signal'][idx_m15] != m1_sig: continue
    
    # H1
    idx_h1 = min(i // 60, len(tf_signals['H1']['signal']) - 1)
    if tf_signals['H1']['confidence'][idx_h1] < CONF_THRESH or tf_signals['H1']['signal'][idx_h1] != m1_sig: continue
    
    h1_trades.append((idx_h1, m1_sig, tf_signals['H1']['price'][idx_h1]))

# حذف تکراری‌ها
unique_h1_trades = []
seen_h1 = set()
for idx, sig, price in h1_trades:
    if idx not in seen_h1:
        seen_h1.add(idx)
        unique_h1_trades.append((idx, sig, price))

print(f"✅ تعداد سیگنال‌های یکتای H1: {len(unique_h1_trades)}")

# بک‌تست H1
print("\n💰 شبیه‌سازی معاملات H1...")
initial_balance = 1000
balance = initial_balance
leverage = 10
sl_pips = 0.0050
tp_pips = 0.0100
win_count = 0
loss_count = 0
prices_h1 = tf_signals['H1']['price']

for idx, signal, entry in unique_h1_trades:
    result = None
    for j in range(1, 6):
        if idx + j >= len(prices_h1): break
        move = (prices_h1[idx + j] - entry) * signal
        if move >= tp_pips:
            result = 'win'
            pnl = tp_pips * balance * leverage * 0.02 / sl_pips
            break
        elif move <= -sl_pips:
            result = 'loss'
            pnl = -sl_pips * balance * leverage * 0.02 / sl_pips
            break
    
    if result is None:
        final_move = (prices_h1[min(idx+5, len(prices_h1)-1)] - entry) * signal
        pnl = final_move * balance * leverage * 0.02 / sl_pips
        result = 'win' if pnl > 0 else 'loss'
    
    balance += pnl
    if result == 'win': win_count += 1
    else: loss_count += 1

print("\n" + "=" * 70)
print("📊 نتایج بک‌تست سیستم سلسله‌مراتبی H1:")
print(f"  موجودی اولیه: ${initial_balance:.2f}")
print(f"  تعداد معاملات: {win_count + loss_count}")
print(f"  برد: {win_count} | باخت: {loss_count}")
if (win_count + loss_count) > 0:
    print(f"  دقت معاملات: {(win_count/(win_count+loss_count)*100):.2f}%")
print(f"  موجودی نهایی: ${balance:.2f}")
print(f"  سود خالص: {((balance - initial_balance) / initial_balance * 100):+.2f}%")
print("=" * 70)
