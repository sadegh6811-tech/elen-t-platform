import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🏆 ربات نهایی H4 (اصلاح‌شده - بدون سرریز عددی)")
print("=" * 70)

def load_data(path):
    df = pd.read_csv(path)
    for c in df.columns:
        if str(c).lower() == 'close':
            return df[c].values
    return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

price = load_data('data/EURUSD_h4.csv')
n = len(price)
print(f"📊 داده H4: {n} کندل")

# ساخت ویژگی‌ها
delta = np.gradient(price)
returns = delta / (price + 1e-9)
buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)
ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
tf_5 = pd.Series(price).rolling(5).mean().bfill().values
tf_15 = pd.Series(price).rolling(15).mean().bfill().values
coherence = 1.0 / (1.0 + np.abs(tf_5 - tf_15))
momentum = pd.Series(price).diff(5).fillna(0).values
vol_60 = pd.Series(returns).rolling(60).std().bfill().values

features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Coherence', 'Vol']
X = np.column_stack([buyer, seller, ent_corr, momentum, coherence, vol_60])
y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, price = X[valid], y_dir[valid], price[valid]
n = len(X)
print(f"📊 داده معتبر: {n} کندل")

# آموزش
split = int(n * 0.6)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
prices_te = price[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("⏳ آموزش مدل GP...")
np.random.seed(42)
random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=50, pop_size=350, max_nodes=15)

if tree is None: sys.exit()

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
signals = np.sign(pred_te)
confidence = np.abs(pred_te)

# ═══════════════════════════════════════════════════════
# 🛠️ بک‌تست با فرمول صحیح (بدون سرریز)
# ═══════════════════════════════════════════════════════
initial_balance = 1000
balance = initial_balance
risk_pct = 0.02
sl_pips = 0.0020
tp_pips = 0.0040

trade_count = 0
win_count = 0
loss_count = 0
max_dd = 0
peak = initial_balance
pnl_history = []

for i in range(len(X_te) - 5):
    if confidence[i] > 0.3 and signals[i] != 0:
        direction = signals[i]
        entry = prices_te[i]
        
        # مقدار ریسک ثابت (۲٪ از موجودی فعلی)
        risk_amount = balance * risk_pct
        
        result = None
        for j in range(1, 6):
            move = (prices_te[i+j] - entry) * direction
            if move >= tp_pips:
                result = 'win'
                pnl = (tp_pips / sl_pips) * risk_amount  # سود = ۲ برابر ریسک
                break
            elif move <= -sl_pips:
                result = 'loss'
                pnl = -risk_amount  # ضرر = مقدار ریسک
                break
        
        if result is None:
            final_move = (prices_te[i+5] - entry) * direction
            pnl = (final_move / sl_pips) * risk_amount
            result = 'win' if pnl > 0 else 'loss'
        
        balance += pnl
        trade_count += 1
        if result == 'win': win_count += 1
        else: loss_count += 1
        
        pnl_history.append(balance)
        
        if balance > peak: peak = balance
        dd = (peak - balance) / peak * 100
        if dd > max_dd: max_dd = dd

print("\n" + "=" * 70)
print("📊 گزارش نهایی (اصلاح‌شده):")
print("=" * 70)
print(f"  💰 موجودی اولیه: ${initial_balance:.2f}")
print(f"  📈 تعداد معاملات: {trade_count}")
print(f"  ✅ برد: {win_count} | ❌ باخت: {loss_count}")
if trade_count > 0:
    print(f"  🎯 دقت معاملات: {(win_count/trade_count)*100:.2f}%")
print(f"  💵 موجودی نهایی: ${balance:.2f}")
print(f"  📈 سود خالص: {((balance - initial_balance) / initial_balance * 100):+.2f}%")
print(f"  📉 Max Drawdown: {max_dd:.2f}%")
print("=" * 70)
