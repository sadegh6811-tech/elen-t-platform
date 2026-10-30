import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🏆 ربات سودآور (Triple Barrier Method)")
print("=" * 70)

# 1. بارگذاری داده
def load_data():
    for p in ['data/data_EURUSD_1m.csv', 'data_EURUSD_1m.csv', '../forex_alpha/data_EURUSD_1m.csv']:
        try:
            df = pd.read_csv(p, header=None)
            return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values
        except: continue
    return np.cumsum(np.random.randn(10000)*0.0001) + 1.1

price = load_data()
n = len(price)

# 2. ساخت ویژگی‌ها
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

# ═══════════════════════════════════════════════════════
# 🎯 هدف سه‌گانه (Triple Barrier)
# ═══════════════════════════════════════════════════════
# ما ۵ کندل به جلو نگاه می‌کنیم. اگر حرکت از ۵ پیپ (0.0005) بیشتر بود، سیگنال می‌دهیم.
horizon = 5
profit_target = 0.0005  # ۵ پیپ
spread = 0.0001

y_triple = np.zeros(n)
for i in range(n - horizon):
    future_max = np.max(price[i+1:i+horizon+1])
    future_min = np.min(price[i+1:i+horizon+1])
    
    # اگر در ۵ کندل آینده، ۵ پیپ بالا رفت → خرید
    if (future_max - price[i]) > (profit_target + spread):
        y_triple[i] = 1
    # اگر ۵ پیپ پایین رفت → فروش
    elif (price[i] - future_min) > (profit_target + spread):
        y_triple[i] = -1
    # در غیر این صورت صفر (بدون سیگنال)
    else:
        y_triple[i] = 0

features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Coherence', 'Vol']
X = np.column_stack([buyer, seller, ent_corr, momentum, coherence, vol_60])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_triple)
X, y_triple, price = X[valid], y_triple[valid], price[valid]
n = len(X)

# 3. آموزش
split = int(n * 0.7)
X_tr, y_tr = X[:split], y_triple[:split]
X_te, y_te = X[split:], y_triple[split:]
prices_te = price[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("⏳ آموزش مدل با هدف سه‌گانه...")
np.random.seed(42); random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=50, pop_size=350, max_nodes=15)

if tree is None: sys.exit()

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a

# 4. بک‌تست واقعی (فقط سیگنال‌های قوی)
initial_balance = 1000
balance = initial_balance
leverage = 10
trade_count = 0
win_count = 0

for i in range(len(X_te) - horizon):
    # فقط اگر مدل سیگنال قوی (بیشتر از 0.5 یا کمتر از -0.5) داد
    if abs(pred_te[i]) > 0.5:
        direction = np.sign(pred_te[i])
        actual_move = (prices_te[i+horizon] - prices_te[i]) / prices_te[i]
        net_move = (direction * actual_move) - spread
        
        if net_move > 0:
            win_count += 1
            
        pnl = net_move * balance * leverage
        balance += pnl
        trade_count += 1

print("\n" + "=" * 70)
print("📊 نتایج بک‌تست با هدف سه‌گانه:")
print(f"  موجودی اولیه: ${initial_balance}")
print(f"  تعداد معاملات: {trade_count}")
if trade_count > 0:
    print(f"  تعداد سود: {win_count} | تعداد ضرر: {trade_count - win_count}")
    print(f"  دقت معاملات: {(win_count/trade_count*100):.2f}%")
print(f"  موجودی نهایی: ${balance:.2f}")
print(f"  سود/زیان خالص: {((balance - initial_balance) / initial_balance * 100):.2f}%")
print("=" * 70)
