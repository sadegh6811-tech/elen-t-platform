import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🎯 ربات Multi-Timeframe: ورود در ۱ دقیقه، نگهداری در ۵ و ۱۵ دقیقه")
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
print(f"📊 داده: {n} کندل ۱ دقیقه")

# 2. ساخت ویژگی‌های ۱ دقیقه (برای تایمینگ دقیق)
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

# هدف: جهت کندل بعدی (برای یادگیری الگوی راس)
y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, price = X[valid], y_dir[valid], price[valid]
n = len(X)

split = int(n * 0.7)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
prices_te = price[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("⏳ آموزش مدل ۱ دقیقه (برای شکار راس)...")
np.random.seed(42); random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=50, pop_size=350, max_nodes=15)
if tree is None: sys.exit()

# پیش‌بینی جهت روی داده تست
pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
signals = np.sign(pred_te)
confidence = np.abs(pred_te)

# ═══════════════════════════════════════════════════════
# 🎯 استراتژی Multi-Timeframe
# ═══════════════════════════════════════════════════════
# فقط زمانی وارد می‌شویم که اطمینان مدل > 0.5 باشد (سیگنال قوی)
# سپس ۵ دقیقه و ۱۵ دقیقه صبر می‌کنیم و خارج می‌شویم.

def backtest_multi_tf(hold_minutes, confidence_threshold=0.5):
    initial_balance = 1000
    balance = initial_balance
    leverage = 10
    spread = 0.0001
    trade_count = 0
    win_count = 0
    loss_count = 0
    max_drawdown = 0
    peak_balance = initial_balance
    trades = []
    
    i = 0
    while i < len(X_te) - hold_minutes:
        # آیا سیگنال قوی داریم؟
        if confidence[i] > confidence_threshold and signals[i] != 0:
            direction = signals[i]
            entry_price = prices_te[i]
            exit_price = prices_te[i + hold_minutes]
            
            # حرکت خالص با احتساب اسپرد
            actual_move = (exit_price - entry_price) / entry_price
            net_move = (direction * actual_move) - spread
            
            # محاسبه PnL
            pnl = net_move * balance * leverage
            balance += pnl
            trade_count += 1
            
            if net_move > 0:
                win_count += 1
            else:
                loss_count += 1
            
            trades.append({
                'index': i,
                'direction': 'BUY' if direction > 0 else 'SELL',
                'entry': entry_price,
                'exit': exit_price,
                'pnl': pnl,
                'confidence': confidence[i]
            })
            
            # به کندل بعدی برو (جلوگیری از معامله تکراری)
            i += hold_minutes
        else:
            i += 1
        
        # محاسبه Max Drawdown
        if balance > peak_balance:
            peak_balance = balance
        drawdown = (peak_balance - balance) / peak_balance * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return {
        'balance': balance,
        'trades': trade_count,
        'wins': win_count,
        'losses': loss_count,
        'pnl_pct': ((balance - initial_balance) / initial_balance) * 100,
        'max_dd': max_drawdown,
        'trade_list': trades
    }

# ═══════════════════════════════════════════════════════
# اجرای بک‌تست در سه تایم‌فریم مختلف
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 نتایج بک‌تست در تایم‌فریم‌های مختلف:")
print("=" * 70)

for hold_min in [1, 5, 15, 30, 60]:
    result = backtest_multi_tf(hold_min, confidence_threshold=0.5)
    
    if result['trades'] > 0:
        accuracy = (result['wins'] / result['trades']) * 100
        emoji = "🏆" if result['pnl_pct'] > 20 else "✅" if result['pnl_pct'] > 0 else "⚠️"
        
        print(f"\n{emoji} نگهداری {hold_min} دقیقه:")
        print(f"   تعداد معاملات: {result['trades']}")
        print(f"   برد: {result['wins']} | باخت: {result['losses']} | دقت: {accuracy:.2f}%")
        print(f"   موجودی نهایی: ${result['balance']:.2f}")
        print(f"   سود/زیان: {result['pnl_pct']:+.2f}%")
        print(f"   Max Drawdown: {result['max_dd']:.2f}%")

print("\n" + "=" * 70)
print("💡 نکته: اگر نگهداری ۱۵ دقیقه سود بیشتری از ۱ دقیقه داشت،")
print("   یعنی استراتژی Multi-Timeframe شما کار می‌کند!")
print("=" * 70)
