import numpy as np
import pandas as pd
import random
import warnings
import os
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🛡️ تست پایداری ۱۰ ساله (H4 با تایید D1)")
print("=" * 70)

def load_data(path):
    if not os.path.exists(path):
        print(f"❌ فایل پیدا نشد: {path}")
        return None
    df = pd.read_csv(path)
    for c in df.columns:
        if str(c).lower() == 'close':
            return df[c].values
    return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

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

# بارگذاری داده‌های ۱۰ ساله
price_h4 = load_data('data/EURUSD_h4.csv')
price_d1 = load_data('data/EURUSD_d1.csv')

if price_h4 is None or price_d1 is None:
    sys.exit()

print(f"📊 H4: {len(price_h4)} کندل (~10 سال)")
print(f"📊 D1: {len(price_d1)} کندل (~10 سال)")

print("\n📊 استخراج سیگنال...")
h4_data = get_signal(price_h4)
d1_data = get_signal(price_d1)

if h4_data is None or d1_data is None:
    print("❌ خطا در استخراج سیگنال.")
    sys.exit()

# شبیه‌سازی
print("\n💰 بک‌تست ۱۰ ساله...")
print("=" * 70)

initial_balance = 1000
balance = initial_balance
risk_amount = 10
tp_pips = 0.0200
sl_pips = 0.0100
conf_thresh = 0.3

n_h4 = len(h4_data['signal'])
trade_count = 0; win_count = 0
last_idx = -10
equity_curve = [initial_balance]
monthly_pnl = {}

for i in range(n_h4 - 30):
    if i - last_idx < 5: continue
    
    h4_sig = h4_data['signal'][i]
    h4_conf = h4_data['confidence'][i]
    
    if h4_conf < conf_thresh or h4_sig == 0: continue
    
    # تایید D1
    d1_idx = min(i // 6, len(d1_data['signal']) - 1)
    d1_sig = d1_data['signal'][d1_idx]
    d1_conf = d1_data['confidence'][d1_idx]
    
    if d1_conf < conf_thresh or d1_sig != h4_sig: continue
    
    direction = h4_sig
    entry = h4_data['price'][i]
    
    result = None
    for j in range(1, 30):
        if i+j >= len(h4_data['price']): break
        move = (h4_data['price'][i+j] - entry) * direction
        if move >= tp_pips:
            result = 'win'; pnl = risk_amount * 2; break
        elif move <= -sl_pips:
            result = 'loss'; pnl = -risk_amount; break
    
    if result is None: continue
    
    balance += pnl
    trade_count += 1
    if result == 'win': win_count += 1
    last_idx = i
    equity_curve.append(balance)
    
    month_key = i // 144
    monthly_pnl[month_key] = monthly_pnl.get(month_key, 0) + pnl

print(f"\n📊 گزارش تست ۱۰ ساله:")
print(f"  💰 موجودی اولیه: ${initial_balance:.2f}")
print(f"  📈 تعداد معاملات: {trade_count}")
print(f"  ✅ برد: {win_count} | ❌ باخت: {trade_count - win_count}")
if trade_count > 0:
    print(f"  🎯 دقت معاملات: {(win_count/trade_count)*100:.2f}%")
print(f"  💵 موجودی نهایی: ${balance:.2f}")
print(f"  📈 سود خالص: {((balance - initial_balance) / initial_balance * 100):+.2f}%")

if len(equity_curve) > 0:
    peak = equity_curve[0]
    max_dd = 0
    for b in equity_curve:
        if b > peak: peak = b
        dd = (peak - b) / peak * 100
        if dd > max_dd: max_dd = dd
    print(f"  📉 Max Drawdown: {max_dd:.2f}%")

print("\n📅 عملکرد ماهانه:")
print("-" * 50)
positive_months = sum(1 for p in monthly_pnl.values() if p > 0)
total_months = len(monthly_pnl)
if total_months > 0:
    print(f"  ماه‌های سودده: {positive_months} از {total_months} ({(positive_months/total_months*100):.1f}%)")
    avg_monthly = sum(monthly_pnl.values()) / total_months
    print(f"  میانگین سود ماهانه: ${avg_monthly:.2f}")

print("=" * 70)

print("\n🎯 نتیجه‌گیری پایداری:")
if balance > initial_balance and (total_months == 0 or positive_months / max(1, total_months) > 0.6):
    print("  🏆 استراتژی در بلندمدت پایدار است!")
elif balance > initial_balance:
    print("  ✅ استراتژی سودآور است، اما نوسانات دارد.")
else:
    print("  ⚠️ استراتژی در بلندمدت ضرر داده.")
print("=" * 70)
