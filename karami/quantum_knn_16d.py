import numpy as np
import pandas as pd
import warnings
import os
warnings.filterwarnings('ignore')

print("🌌 مدل همسایگی کوانتومی در بعد ۱۶ (Quantum KNN)")
print("=" * 70)

# 1. بارگذاری داده H4
def load_data(path):
    df = pd.read_csv(path)
    cols = {str(c).lower(): c for c in df.columns}
    c = df[cols.get('close', df.columns[3])].values
    return c

price = load_data('data/EURUSD_h4.csv')
n = len(price)
print(f"📊 داده H4: {n} کندل")

# 2. ساخت فضای ۱۶ بعدی (ویژگی‌ها)
# برای جلوگیری از نشت، همه چیز را شیفت می‌دهیم (فقط گذشته)
delta = np.zeros(n)
delta[1:] = price[1:] - price[:-1]
returns = delta / (price + 1e-9)

buyer = np.where(delta > 0, delta, 0)
seller = np.where(delta < 0, np.abs(delta), 0)

# شیفت دادن به عقب (تا از آینده استفاده نکنیم)
buyer = np.roll(buyer, 1); buyer[0] = 0
seller = np.roll(seller, 1); seller[0] = 0

# تایم‌فریم‌ها
tf_5 = pd.Series(price).rolling(5).mean().shift(1).bfill().values
tf_15 = pd.Series(price).rolling(15).mean().shift(1).bfill().values
tf_60 = pd.Series(price).rolling(60).mean().shift(1).bfill().values

# درهم‌تنیدگی (Entanglement)
ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values

# آنتروپی
def shannon_entropy(ret, w=20):
    e = np.zeros(len(ret))
    for i in range(w, len(ret)):
        data = ret[i-w:i]
        if np.all(data == data[0]): continue
        hist, _ = np.histogram(data, bins=10)
        probs = hist / (hist.sum() + 1e-9)
        probs = probs[probs > 0]
        e[i] = -np.sum(probs * np.log2(probs))
    return e

entropy = shannon_entropy(np.roll(returns, 1))

# ماتریس ۱۶ بعدی
features = ['Buyer', 'Seller', 'Ent', 'TF5', 'TF15', 'TF60', 'Entropy', 'Momentum']
X = np.column_stack([buyer, seller, ent_corr, tf_5, tf_15, tf_60, entropy, np.roll(delta, 1)])

# نرمال‌سازی (برای اینکه فاصله‌ها معنی‌دار باشند)
X_mean = np.mean(X, axis=0)
X_std = np.std(X, axis=0) + 1e-9
X_norm = (X - X_mean) / X_std

# هدف: جهت کندل بعدی
y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

# 3. تقسیم داده (۶۰٪ آموزش برای ساخت حافظه، ۴۰٪ تست)
split = int(n * 0.6)
X_train = X_norm[:split]
y_train = y_dir[:split]
X_test = X_norm[split:]
y_test = y_dir[split:]
price_test = price[split:]

print(f"📊 داده آموزش: {len(X_train)} | داده تست: {len(X_test)}")

# 4. الگوریتم KNN دستی (بدون sklearn)
def predict_knn(X_test_point, X_train, y_train, k=100):
    """فاصله اقلیدسی تا همه نقاط آموزش و پیدا کردن k نزدیک‌ترین"""
    # محاسبه فاصله اقلیدسی
    distances = np.sqrt(np.sum((X_train - X_test_point)**2, axis=1))
    
    # پیدا کردن k نزدیک‌ترین
    k_indices = np.argsort(distances)[:k]
    k_labels = y_train[k_indices]
    
    # رای‌گیری
    up_votes = np.sum(k_labels == 1)
    down_votes = np.sum(k_labels == -1)
    
    total = up_votes + down_votes
    if total == 0: return 0, 0.0
    
    if up_votes > down_votes:
        return 1, up_votes / total
    elif down_votes > up_votes:
        return -1, down_votes / total
    else:
        return 0, 0.0

# 5. شبیه‌سازی
print("\n⏳ اجرای مدل KNN در بعد ۱۶ (چند لحظه صبر کنید)...")
initial_balance = 1000
balance = initial_balance
k_neighbors = 50  # تعداد همسایه‌ها در فضای ۱۶ بعدی
confidence_threshold = 0.90  # حداقل ۹۰٪ اطمینان برای معامله

trade_count = 0
win_count = 0
profit_pips = 0
equity = [initial_balance]

# برای سرعت، فقط ۵۰۰ کندل آخر را تست می‌کنیم
start_test = max(0, len(X_test) - 500)
for i in range(start_test, len(X_test) - 1):
    signal, confidence = predict_knn(X_test[i], X_train, y_train, k=k_neighbors)
    
    if confidence >= confidence_threshold and signal != 0:
        # حرکت واقعی در کندل بعدی (به پیپ)
        actual_move = (price_test[i+1] - price_test[i]) * 10000
        trade_pips = actual_move * signal
        
        # کسر اسپرد (۱.۵ پیپ)
        trade_pips -= 1.5
        
        profit_pips += trade_pips
        trade_count += 1
        
        if trade_pips > 0:
            win_count += 1
            
        # شبیه‌سازی سرمایه (با اهرم ۱۰، ریسک ۲٪)
        balance += trade_pips * 0.2  # تقریبی
        equity.append(balance)

print("\n" + "=" * 70)
print(f"📊 نتایج مدل KNN در بعد ۱۶:")
print(f"  🔍 تعداد همسایه‌ها (k): {k_neighbors}")
print(f"  🎯 آستانه اطمینان: {confidence_threshold*100:.0f}%")
print(f"  📈 تعداد معاملات: {trade_count}")
if trade_count > 0:
    print(f"  ✅ برد: {win_count} | ❌ باخت: {trade_count - win_count}")
    print(f"  🎯 دقت: {(win_count/trade_count*100):.2f}%")
    print(f"  💰 مجموع سود (پیپ): {profit_pips:+.1f}")
    print(f"  💵 موجودی نهایی: ${balance:.2f}")
    print(f"  📈 سود خالص: {((balance - initial_balance)/initial_balance*100):+.2f}%")
else:
    print("  ⚠️ هیچ معامله‌ای با این آستانه اطمینان پیدا نشد.")
print("=" * 70)

# آمار توزیع اطمینان
print("\n📊 توزیع اطمینان در فضای ۱۶ بعدی:")
conf_list = []
for i in range(start_test, len(X_test) - 1):
    _, conf = predict_knn(X_test[i], X_train, y_train, k=k_neighbors)
    conf_list.append(conf)

if conf_list:
    conf_arr = np.array(conf_list)
    print(f"  میانگین اطمینان: {np.mean(conf_arr)*100:.1f}%")
    print(f"  حداکثر اطمینان: {np.max(conf_arr)*100:.1f}%")
    print(f"  تعداد سیگنال‌های با اطمینان >90%: {np.sum(conf_arr > 0.9)}")
    print(f"  تعداد سیگنال‌های با اطمینان >95%: {np.sum(conf_arr > 0.95)}")
    print(f"  تعداد سیگنال‌های با اطمینان >99%: {np.sum(conf_arr > 0.99)}")
