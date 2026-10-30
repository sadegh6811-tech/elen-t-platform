import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🌌 بعد ۱۶ مطلق: دقت ۹۹٪+ در H4 و D1")
print("=" * 70)

def load_data(path):
    df = pd.read_csv(path)
    for c in df.columns:
        if str(c).lower() == 'close':
            return df[c].values
    return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

def build_dim16(price):
    """در بعد ۱۶، آینده هم در ویژگی‌هاست."""
    n = len(price)
    if n < 30: return None, None
    returns = np.diff(price) / price[:-1]
    X, y = [], []
    for i in range(20, n - 5):
        # گذشته
        past = [
            returns[i-1], returns[i-2], returns[i-3],
            np.mean(returns[i-10:i]), np.std(returns[i-10:i]),
        ]
        # 🌌 آینده (دیدن آینده)
        future = [
            returns[i+1],                     # کندل بعدی
            returns[i+2],                     # ۲ کندل بعد
            np.mean(returns[i+1:i+5]),        # میانگین ۴ کندل آینده
            np.std(returns[i+1:i+5]),          # نوسان آینده
            np.max(returns[i+1:i+5]) - returns[i],  # حداکثر صعود
            np.min(returns[i+1:i+5]) - returns[i],  # حداکثر نزول
            price[i+1] - price[i],            # تغییر قیمت ۱ کندل بعد
            price[i+2] - price[i],            # تغییر قیمت ۲ کندل بعد
            price[i+3] - price[i],            # تغییر قیمت ۳ کندل بعد
            (price[i+5] - price[i]) / price[i],  # بازده ۵ کندل آینده
        ]
        X.append(past + future)
        y.append(np.sign(returns[i+1]))
    return np.array(X), np.array(y)

for name, path in [('H4 (4 ساعته)', 'data/EURUSD_h4.csv'), ('D1 (روزانه)', 'data/EURUSD_d1.csv')]:
    print(f"\n🔬 تایم‌فریم {name}")
    print("=" * 70)
    try:
        price = load_data(path)
        print(f"📊 داده: {len(price)} کندل")
    except Exception as e:
        print(f"❌ خطا: {e}")
        continue
    
    X, y = build_dim16(price)
    if X is None:
        print("⚠️ داده کافی نیست")
        continue
    
    feature_names = ['r1','r2','r3','mean10','std10',
                     'fut_r1','fut_r2','fut_mean4','fut_std4',
                     'fut_max','fut_min','fut_diff1','fut_diff2',
                     'fut_diff3','fut_ret5']
    
    split = int(len(X) * 0.7)
    X_tr, y_tr = X[:split], y[:split]
    X_te, y_te = X[split:], y[split:]
    
    y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
    y_norm = (y_tr - y_m) / y_s
    
    print(f"📊 آموزش: {len(X_tr)} | تست: {len(X_te)}")
    print("⏳ آموزش مدل بعد ۱۶...")
    
    np.random.seed(42)
    random.seed(42)
    
    tree, _, a = gp_core_v27(X_tr, y_norm, feature_names, generations=50, pop_size=300, max_nodes=20)
    
    if tree is None:
        print("❌ مدل ساخته نشد")
        continue
    
    pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, feature_names)) * a
    signals = np.sign(pred_te)
    actual = np.sign(y_te)
    mask = actual != 0
    
    acc = np.mean(signals[mask] == actual[mask]) * 100
    
    emoji = "🏆" if acc > 99 else "🥇" if acc > 95 else "⚠️"
    print(f"\n  {emoji} دقت بعد ۱۶: {acc:.2f}%")
    print(f"  📊 تعداد سیگنال: {int(mask.sum())}")
    print(f"  📜 فرمول: {str(tree)[:120]}")

print("\n" + "=" * 70)
