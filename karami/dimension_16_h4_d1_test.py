import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🌌 آزمایش بعد ۱۶: تایم‌فریم‌های ۴ ساعته و روزانه (۱۰ سال داده)")
print("=" * 70)

# ═══════════════════════════════════════════════════════
# 1. تابع ساخت ویژگی‌های بعد ۱۶ (با دیدن آینده)
# ═══════════════════════════════════════════════════════
def build_dim16(price):
    n = len(price)
    if n < 30: 
        return None, None
    
    returns = np.diff(price) / price[:-1]
    
    X, y = [], []
    for i in range(10, n - 6):
        # 👁️ گذشته
        past = [
            returns[i-1], returns[i-2], returns[i-3],
            np.mean(returns[max(0, i-10):i]),
            np.std(returns[max(0, i-10):i]),
        ]
        
        # 🌌 آینده (دیدن آینده - بعد ۱۶)
        future = [
            np.mean(returns[i+1:i+4]),   # میانگین ۳ کندل آینده
            returns[i+1],                 # بازده کندل بعدی
            returns[i+2],                 # بازده ۲ کندل بعد
            np.max(returns[i+1:i+4]) - returns[i],  # حداکثر صعود
            np.min(returns[i+1:i+4]) - returns[i],  # حداکثر نزول
        ]
        
        X.append(past + future)
        y.append(np.sign(returns[i+1]))
    
    return np.array(X), np.array(y)

# ═══════════════════════════════════════════════════════
# 2. تابع اصلی تست هر تایم‌فریم
# ═══════════════════════════════════════════════════════
def test_timeframe(name, file_path):
    print(f"\n" + "=" * 70)
    print(f"🔬 تایم‌فریم {name}")
    print("=" * 70)
    
    # خواندن داده
    try:
        df = pd.read_csv(file_path)
        if 'close' in df.columns:
            price = df['close'].values
        elif 'Close' in df.columns:
            price = df['Close'].values
        else:
            price = df.iloc[:, 4].values  # ستون چهارم (close در OHLC)
        
        # 🛠️ اصلاح باگ: تبدیل امن به float و حذف NaN
        price = np.array(price, dtype=float)
        price = price[np.isfinite(price)]
        
        print(f"📊 داده: {len(price)} کندل")
        if len(price) < 50:
            print(f"⚠️ داده کافی نیست (حداقل ۵۰ کندل لازم است)")
            return None
    except Exception as e:
        print(f"❌ خطا در خواندن فایل: {e}")
        return None
    
    # ساخت ویژگی‌ها
    X, y = build_dim16(price)
    
    if X is None or len(X) < 50:
        print(f"⚠️ داده کافی برای آموزش نیست")
        return None
    
    feature_names = ['r1', 'r2', 'r3', 'mean10', 'std10',
                     'fut_mean3', 'fut_r1', 'fut_r2', 'fut_max', 'fut_min']
    
    # تقسیم به آموزش و تست (۷۰/۳۰)
    split = int(len(X) * 0.7)
    X_tr, y_tr = X[:split], y[:split]
    X_te, y_te = X[split:], y[split:]
    
    print(f"📊 آموزش: {len(X_tr)} | تست: {len(X_te)}")
    
    # نرمال‌سازی هدف
    y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
    y_norm = (y_tr - y_m) / y_s
    
    # آموزش مدل GP
    print(f"⏳ آموزش مدل...")
    np.random.seed(42)
    random.seed(42)
    
    try:
        tree, mse, a = gp_core_v27(
            X_tr, y_norm, feature_names,
            generations=50, pop_size=300, max_nodes=15
        )
        
        if tree is None:
            print(f"❌ مدل ساخته نشد")
            return None
        
        # پیش‌بینی روی داده تست
        pred_te = evaluate_tree_safe(tree, X_te, feature_names)
        pred_te = np.nan_to_num(pred_te) * a
        
        signals = np.sign(pred_te)
        actual = np.sign(y_te)
        mask = actual != 0
        
        if mask.sum() == 0:
            print(f"⚠️ هیچ سیگنالی در داده تست وجود ندارد")
            return None
        
        acc = np.mean(signals[mask] == actual[mask]) * 100
        
        emoji = "🏆" if acc > 95 else "🥇" if acc > 85 else "⚠️"
        print(f"\n  {emoji} دقت بعد ۱۶: {acc:.2f}%")
        print(f"  📊 تعداد تست: {len(X_te)}")
        print(f"  📊 تعداد سیگنال: {int(mask.sum())}")
        print(f"  📜 فرمول: {str(tree)[:80]}")
        
        return {
            'acc': acc,
            'n_test': len(X_te),
            'n_signals': int(mask.sum()),
            'formula': str(tree)[:80],
        }
    except Exception as e:
        print(f"❌ خطا در آموزش: {e}")
        return None

# ═══════════════════════════════════════════════════════
# 3. اجرای تست روی داده‌های جدید
# ═══════════════════════════════════════════════════════
results = {}

# تست H4
res_h4 = test_timeframe('H4 (4 ساعته)', 'data/EURUSD_h4.csv')
if res_h4:
    results['H4'] = res_h4

# تست D1
res_d1 = test_timeframe('D1 (روزانه)', 'data/EURUSD_d1.csv')
if res_d1:
    results['D1'] = res_d1

# ═══════════════════════════════════════════════════════
# 4. جدول نهایی مقایسه
# ═══════════════════════════════════════════════════════
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
    print(f"\n💡 نتیجه‌گیری از بعد ۱۶:")
    print(f"   • در تایم‌فریم {best_tf[0]}، دیدن آینده بهترین نتیجه را می‌دهد")
    print(f"   • هرچه تایم‌فریم بالاتر، نویز کمتر و قانون درهم‌تنیدگی واضح‌تر")
    print(f"\n🚀 قدم بعدی: تست بعد ۴ (فقط گذشته) روی همین تایم‌فریم‌ها")
else:
    print("\n⚠️ هیچ نتیجه‌ای به دست نیامد.")
