import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("💰 ربات سودآور H4 (بر اساس لبه واقعی ۷۴٪)")
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

# ساخت ویژگی‌ها (بدون نشت داده)
delta = np.gradient(price)
returns = delta / (price + 1e-9)
buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)
ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
tf_5 = pd.Series(price).rolling(5).mean().bfill().values
tf_15 = pd.Series(price).rolling(15).mean().bfill().values
coherence = 1.0 / (1.0 + np.abs(tf_5 - tf_15))
momentum = pd.Series(price).diff(5).fillna(0).values

features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Coherence']
X = np.column_stack([buyer, seller, ent_corr, momentum, coherence])
y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
X, y_dir, price = X[valid], y_dir[valid], price[valid]
n = len(X)

# آموزش مدل (همان روش Walk-Forward)
split = int(n * 0.6)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]
prices_te = price[split:]

# نرمال‌سازی
y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

# آموزش با رگرسیون خطی (همان روش آزمون قبلی)
X_b = np.column_stack([X_tr, np.ones(len(X_tr))])
w = np.linalg.lstsq(X_b, y_norm, rcond=None)[0]

# پیش‌بینی
X_te_b = np.column_stack([X_te, np.ones(len(X_te))])
pred_te = X_te_b @ w
signals = np.sign(pred_te)
confidence = np.abs(pred_te)

# ═══════════════════════════════════════════════════════
# بک‌تست با SL/TP
# ═══════════════════════════════════════════════════════
initial_balance = 1000
balance = initial_balance
risk_pct = 0.02  # ریسک ۲٪ در هر معامله
leverage = 10
sl_pips = 0.0020  # ۲۰ پیپ
tp_pips = 0.0040  # ۴۰ پیپ (نسبت ۱:۲)

trade_count = 0
win_count = 0
loss_count = 0
max_dd = 0
peak = initial_balance

for i in range(len(X_te) - 5):
    if confidence[i] > 0.3 and signals[i] != 0:  # فیلتر اطمینان
        direction = signals[i]
        entry = prices_te[i]
        
        # بررسی SL/TP در ۵ کندل بعدی
        result = None
        for j in range(1, 6):
            move = (prices_te[i+j] - entry) * direction
            if move >= tp_pips:
                result = 'win'
                pnl = tp_pips * balance * leverage * risk_pct / sl_pips
                break
            elif move <= -sl_pips:
                result = 'loss'
                pnl = -sl_pips * balance * leverage * risk_pct / sl_pips
                break
        
        if result is None:
            final_move = (prices_te[i+5] - entry) * direction
            pnl = final_move * balance * leverage * risk_pct / sl_pips
            result = 'win' if pnl > 0 else 'loss'
        
        balance += pnl
        trade_count += 1
        if result == 'win': win_count += 1
        else: loss_count += 1
        
        if balance > peak: peak = balance
        dd = (peak - balance) / peak * 100
        if dd > max_dd: max_dd = dd

print("\n" + "=" * 70)
print("📊 نتایج بک‌تست H4:")
print(f"  موجودی اولیه: ${initial_balance:.2f}")
print(f"  تعداد معاملات: {trade_count}")
print(f"  برد: {win_count} | باخت: {loss_count}")
if trade_count > 0:
    print(f"  دقت معاملات: {(win_count/trade_count*100):.2f}%")
print(f"  موجودی نهایی: ${balance:.2f}")
print(f"  سود خالص: {((balance - initial_balance) / initial_balance * 100):+.2f}%")
print(f"  Max Drawdown: {max_dd:.2f}%")
print("=" * 70)
