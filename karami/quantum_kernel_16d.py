import numpy as np
import pandas as pd
import warnings
import os
warnings.filterwarnings('ignore')

print("🌌 مدل هسته گاوسی در بعد ۱۶ (تقریب فضای پیوسته)")
print("=" * 70)

# 🚀 اصلاح مسیر فایل: جستجو در چندین مکان
def find_file(filename):
    possible_paths = [
        filename,  # مسیر فعلی
        os.path.join(os.path.expanduser('~'), 'karami', filename),  # پوشه karami
        os.path.join(os.path.expanduser('~'), 'karami', 'data', os.path.basename(filename)),  # پوشه karami/data
        os.path.join(os.path.expanduser('~'), 'elen', filename),  # پوشه elen
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None

file_path = find_file('data/EURUSD_h4.csv')
if file_path is None:
    file_path = find_file('EURUSD_h4.csv')

if file_path is None:
    print("❌ فایل داده H4 در هیچ‌کدام از مسیرهای زیر پیدا نشد:")
    print("   - ./data/EURUSD_h4.csv")
    print("   - ~/karami/data/EURUSD_h4.csv")
    print("   - ~/karami/EURUSD_h4.csv")
    print("\nلطفاً ابتدا فایل را دانلود کنید یا مسیر آن را بررسی کنید.")
    exit()

print(f"✅ فایل داده در مسیر {file_path} پیدا شد.")

# 1. بارگذاری داده H4
def load_data(path):
    df = pd.read_csv(path)
    cols = {str(c).lower(): c for c in df.columns}
    c = df[cols.get('close', df.columns[3])].values
    return c

price = load_data(file_path)
n = len(price)
print(f"📊 داده H4: {n} کندل")

# 2. ساخت ویژگی‌ها (بدون نشت آینده)
delta = np.zeros(n)
delta[1:] = price[1:] - price[:-1]
returns = delta / (price + 1e-9)

buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)
buyer = np.roll(buyer, 1); buyer[0] = 0
seller = np.roll(seller, 1); seller[0] = 0

tf_5 = pd.Series(price).rolling(5).mean().shift(1).bfill().values
tf_15 = pd.Series(price).rolling(15).mean().shift(1).bfill().values
tf_60 = pd.Series(price).rolling(60).mean().shift(1).bfill().values

ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values

momentum = pd.Series(price).diff(5).fillna(0).values
momentum = np.roll(momentum, 1); momentum[0] = 0

features = ['Buyer', 'Seller', 'Ent', 'TF5', 'TF15', 'TF60', 'Mom']
X = np.column_stack([buyer, seller, ent_corr, tf_5, tf_15, tf_60, momentum])

# نرمال‌سازی
X_mean = np.mean(X, axis=0)
X_std = np.std(X, axis=0) + 1e-9
X_norm = (X - X_mean) / X_std

# هدف
y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

split = int(n * 0.6)
X_train = X_norm[:split]
y_train = y_dir[:split]
X_test = X_norm[split:]
y_test = y_dir[split:]
price_test = price[split:]

print(f"📊 آموزش: {len(X_train)} | تست: {len(X_test)}")

# 3. 🚀 هسته گاوسی (RBF Kernel)
def rbf_kernel(X1, X2, gamma=1.0):
    X1_sq = np.sum(X1**2, axis=1).reshape(-1, 1)
    X2_sq = np.sum(X2**2, axis=1).reshape(1, -1)
    sq_dist = X1_sq + X2_sq - 2 * np.dot(X1, X2.T)
    return np.exp(-gamma * sq_dist)

gamma = 0.1
print(f"\n🌐 محاسبه هسته گاوسی (gamma={gamma})...")

K_train = rbf_kernel(X_train, X_train, gamma)
K_test = rbf_kernel(X_test, X_train, gamma)

# 4. رگرسیون کرنل
print("\n⏳ آموزش مدل در فضای بی‌نهایت بعدی...")
lambda_reg = 1e-3
I = np.eye(K_train.shape[0])
alpha = np.linalg.solve(K_train + lambda_reg * I, y_train)

predictions = K_test @ alpha
signals = np.sign(predictions)
confidence = np.abs(predictions)

print("\n✅ آموزش کامل شد.")

# 5. ارزیابی
mask = y_test != 0
accuracy = np.mean(signals[mask] == y_test[mask]) * 100
print(f"\n📊 دقت در فضای هسته گاوسی: {accuracy:.2f}%")

# 6. بک‌تست تجاری
print("\n" + "=" * 70)
print("💰 بک‌تست با هسته درهم‌تنیده:")

initial_balance = 1000
tp_pips = 0.0200
sl_pips = 0.0100
spread = 0.00015

confidence_thresholds = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7]

for conf_thresh in confidence_thresholds:
    balance = initial_balance
    trade_count = 0
    win_count = 0
    
    for i in range(len(X_test) - 5):
        if confidence[i] < conf_thresh or signals[i] == 0: continue
        
        direction = signals[i]
        entry = price_test[i] + (spread if direction == 1 else -spread)
        
        result = None
        for j in range(1, 6):
            if i+j >= len(price_test): break
            move = (price_test[i+j] - entry) * direction
            if move >= tp_pips:
                result = 'win'; break
            elif move <= -sl_pips:
                result = 'loss'; break
        
        if result is None: continue
        
        risk_amount = balance * 0.01
        pnl = risk_amount * 2 if result == 'win' else -risk_amount
        balance += pnl
        trade_count += 1
        if result == 'win': win_count += 1
    
    profit_pct = (balance - initial_balance) / initial_balance * 100
    emoji = "🏆" if profit_pct > 50 else "✅" if profit_pct > 0 else "⚠️"
    
    print(f"  {emoji} آستانه {conf_thresh:.1f} | معاملات: {trade_count} | دقت: {(win_count/max(1,trade_count)*100):.1f}% | سود: {profit_pct:+.1f}%")

print("=" * 70)
