import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🌌 آزمایش بعد ۱۶: تایم‌فریم‌های ۴ ساعته و روزانه")
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

# 2. تبدیل به تایم‌فریم‌های بالاتر
def resample(price_1m, minutes):
    n = len(price_1m) // minutes * minutes
    if n < minutes * 10:
        return np.array([])
    reshaped = price_1m[:n].reshape(-1, minutes)
    return reshaped[:, -1]  # Close

timeframes = {
    '4H (240min)': resample(price_1m, 240),
    '1D (1440min)': resample(price_1m, 1440),
}

# 3. تابع ساخت ویژگی‌های بعد ۱۶
def build_dim16(price):
    n = len(price)
    if n < 30: return None, None
    
    returns = np.diff(price) / price[:-1]
    
    X, y = [], []
    for i in range(10, n - 6):
        past = [
            returns[i-1], returns[i-2], returns[i-3],
            np.mean(returns[max(0, i-10):i]),
            np.std(returns[max(0, i-10):i]),
        ]
        
        future = [
            np.mean(returns[i+1:i+4]),  # میانگین ۳ کندل آینده
            returns[i+1],                # بازده کندل بعدی
            returns[i+2],                # بازده ۲ کندل بعد
            np.max(returns[i+1:i+4]) - returns[i],
            np.min(returns[i+1:i+4]) - returns[i],
        ]
        
        X.append(past + future)
        y.append(np.sign(returns[i+1]))
    
    return np.array(X), np.array(y)

# 4. تست هر تایم‌فریم
results = {}

for tf_name, price in timeframes.items():
    if len(price) < 30:
        print(f"\n⚠️ {tf_name}: داده کافی نیست ({len(price)} کندل)")
        continue
    
    print(f"\n" + "=" * 70)
    print(f"🔬 تایم‌فریم {tf_name} ({len(price)} کندل)")
    print("=" * 70)
    
    X, y = build_dim16(price)
    
    if X is None or len(X) < 20:
        print(f"⚠️ داده کافی برای آموزش نیست")
        continue
    
    feature_names = ['r1', 'r2', 'r3', 'mean10', 'std10',
                     'fut_mean3', 'fut_r1', 'fut_r2', 'fut_max', 'fut_min']
    
    # تقسیم
    split = int(len(X) * 0.7)
    if split < 10:
        print("⚠️ داده آموزش کافی نیست")
        continue
    
    X_tr, y_tr = X[:split], y[:split]
    X_te, y_te = X[split:], y[split:]
    
    # نرمال‌سازی
    y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
    y_norm = (y_tr - y_m) / y_s
    
    # آموزش
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
        
        # پیش‌بینی
        pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, feature_names)) * a
        signals = np.sign(pred_te)
        actual = np.sign(y_te)
        mask = actual != 0
        
        if mask.sum() == 0:
            print(f"⚠️ {tf_name}: هیچ سیگنالی در تست وجود ندارد")
            continue
        
        acc = np.mean(signals[mask] == actual[mask]) * 100
        
        results[tf_name] = {
            'acc': acc,
            'n_test': len(X_te),
            'n_signals': int(mask.sum()),
            'formula': str(tree)[:60],
        }
        
        emoji = "🏆" if acc > 95 else "🥇" if acc > 85 else "⚠️"
        print(f"  {emoji} دقت بعد ۱۶: {acc:.2f}%")
        print(f"  📊 تعداد تست: {len(X_te)} کندل")
        print(f"  📊 تعداد سیگنال: {mask.sum()}")
        print(f"  📜 فرمول: {str(tree)[:60]}...")
        
    except Exception as e:
        print(f"❌ خطا در {tf_name}: {e}")
        continue

# 5. جدول نهایی
print("\n" + "=" * 70)
print("📊 جدول نهایی: بعد ۱۶ در تایم‌فریم‌های بالا")
print("=" * 70)
print(f"{'تایم‌فریم':<15} | {'دقت':<10} | {'تعداد تست':<12} | {'وضعیت':<10}")
print("-" * 70)

for tf_name, res in results.items():
    emoji = "🏆" if res['acc'] > 95 else "🥇" if res['acc'] > 85 else "⚠️"
    status = "عالی" if res['acc'] > 95 else "خوب" if res['acc'] > 85 else "ضعیف"
    print(f"{tf_name:<15} | {res['acc']:>6.2f}%  | {res['n_test']:>8}     | {emoji} {status}")

print("=" * 70)

if results:
    best_tf = max(results.items(), key=lambda x: x[1]['acc'])
    print(f"\n🏆 بهترین تایم‌فریم: {best_tf[0]} با دقت {best_tf[1]['acc']:.2f}%")
