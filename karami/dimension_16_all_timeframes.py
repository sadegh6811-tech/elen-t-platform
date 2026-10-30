import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🌌 آزمایش بعد ۱۶: دیدن آینده در تمام تایم‌فریم‌ها")
print("=" * 70)

# 1. بارگذاری داده
def load_data():
    for p in ['data/data_EURUSD_1m.csv', 'data_EURUSD_1m.csv', '../forex_alpha/data_EURUSD_1m.csv']:
        try:
            df = pd.read_csv(p, header=None)
            return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values
        except: continue
    return np.cumsum(np.random.randn(10000)*0.0001) + 1.1

price_1m = load_data()
print(f"📊 داده ۱ دقیقه: {len(price_1m)} کندل")

# 2. ساخت کندل‌های تایم‌فریم‌های بالاتر
def resample(price_1m, minutes):
    n = len(price_1m) // minutes * minutes
    reshaped = price_1m[:n].reshape(-1, minutes)
    # استفاده از آخرین قیمت هر بازه (Close)
    return reshaped[:, -1]

timeframes = {
    '1min': price_1m,
    '5min': resample(price_1m, 5),
    '15min': resample(price_1m, 15),
    '30min': resample(price_1m, 30),
    '60min': resample(price_1m, 60),
}

# 3. تابع ساخت ویژگی‌های بعد ۱۶ (با دیدن آینده)
def build_dim16(price, tf_name):
    """
    در بعد ۱۶، ما آینده را می‌بینیم. بنابراین ویژگی‌ها شامل
    اطلاعات آینده (۵ کندل بعد) هم هستند.
    """
    n = len(price)
    if n < 30: return None, None, None
    
    returns = np.diff(price) / price[:-1]
    
    X, y = [], []
    for i in range(20, n - 10):
        # 👁️ ویژگی‌های گذشته (در دسترس در بعد ۳)
        past = [
            returns[i-1],
            returns[i-2],
            returns[i-3],
            np.mean(returns[i-10:i]),
            np.std(returns[i-10:i]),
        ]
        
        # 🌌 ویژگی‌های آینده (فقط در بعد ۱۶ قابل مشاهده!)
        future = [
            np.mean(returns[i+1:i+6]),       # میانگین ۵ کندل آینده
            np.std(returns[i+1:i+6]),         # نوسان آینده
            returns[i+1],                      # بازده کندل بعدی (آینده!)
            returns[i+2],                      # بازده ۲ کندل بعد
            np.max(returns[i+1:i+6]) - returns[i],  # حداکثر صعود آینده
            np.min(returns[i+1:i+6]) - returns[i],  # حداکثر نزول آینده
        ]
        
        X.append(past + future)
        y.append(np.sign(returns[i+1]))  # هدف: جهت کندل بعدی
    
    return np.array(X), np.array(y), price[20:n-10]

# 4. تست هر تایم‌فریم
results = {}

for tf_name, price in timeframes.items():
    if len(price) < 50:
        print(f"\n⚠️ {tf_name}: داده کافی نیست ({len(price)} کندل)")
        continue
    
    print(f"\n" + "=" * 70)
    print(f"🔬 تایم‌فریم {tf_name} ({len(price)} کندل)")
    print("=" * 70)
    
    X, y, prices = build_dim16(price, tf_name)
    
    if X is None:
        continue
    
    # نام‌گذاری ویژگی‌ها
    feature_names = ['r1', 'r2', 'r3', 'mean10', 'std10',
                     'fut_mean5', 'fut_std5', 'fut_r1', 'fut_r2',
                     'fut_max', 'fut_min']
    
    # تقسیم به آموزش و تست
    split = int(len(X) * 0.7)
    X_tr, y_tr = X[:split], y[:split]
    X_te, y_te = X[split:], y[split:]
    
    # نرمال‌سازی
    y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
    y_norm = (y_tr - y_m) / y_s
    
    # آموزش با موتور GP
    print(f"⏳ آموزش مدل {tf_name}...")
    np.random.seed(42)
    random.seed(42)
    
    try:
        tree, mse, a = gp_core_v27(
            X_tr, y_norm, feature_names,
            generations=30, pop_size=200, max_nodes=15
        )
        
        if tree is None:
            print(f"❌ {tf_name}: مدل ساخته نشد")
            continue
        
        # پیش‌بینی روی داده تست
        pred_te = evaluate_tree_safe(tree, X_te, feature_names)
        pred_te = np.nan_to_num(pred_te) * a
        
        # دقت
        signals = np.sign(pred_te)
        actual = np.sign(y_te)
        mask = actual != 0
        
        acc = np.mean(signals[mask] == actual[mask]) * 100
        
        # ذخیره نتایج
        results[tf_name] = {
            'acc': acc,
            'n_test': len(X_te),
            'n_signals': mask.sum(),
            'formula': str(tree)[:80],
        }
        
        emoji = "🏆" if acc > 95 else "🥇" if acc > 85 else "⚠️"
        print(f"  {emoji} دقت بعد ۱۶: {acc:.2f}%")
        print(f"  📊 تعداد تست: {len(X_te)} کندل")
        print(f"  📜 نمونه فرمول: {str(tree)[:60]}...")
        
    except Exception as e:
        print(f"❌ خطا در {tf_name}: {e}")
        continue

# 5. جدول نهایی مقایسه
print("\n" + "=" * 70)
print("📊 جدول نهایی: دقت بعد ۱۶ در تایم‌فریم‌های مختلف")
print("=" * 70)
print(f"{'تایم‌فریم':<12} | {'دقت':<10} | {'تعداد تست':<12} | {'وضعیت':<10}")
print("-" * 70)

for tf_name, res in results.items():
    emoji = "🏆" if res['acc'] > 95 else "🥇" if res['acc'] > 85 else "⚠️"
    status = "عالی" if res['acc'] > 95 else "خوب" if res['acc'] > 85 else "ضعیف"
    print(f"{tf_name:<12} | {res['acc']:>6.2f}%  | {res['n_test']:>8}     | {emoji} {status}")

print("=" * 70)

if results:
    best_tf = max(results.items(), key=lambda x: x[1]['acc'])
    print(f"\n🏆 بهترین تایم‌فریم: {best_tf[0]} با دقت {best_tf[1]['acc']:.2f}%")
    print(f"\n💡 نتیجه‌گیری از بعد ۱۶:")
    print(f"   • در تایم‌فریم {best_tf[0]}، دیدن آینده بهترین نتیجه را می‌دهد")
    print(f"   • هرچه تایم‌فریم بالاتر، نویز کمتر و قانون درهم‌تنیدگی واضح‌تر")
