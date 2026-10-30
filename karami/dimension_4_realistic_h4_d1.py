import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🔒 آزمایش بعد ۴: فقط از گذشته برای پیش‌بینی آینده (H4 و D1)")
print("=" * 70)

def build_dim4(price):
    n = len(price)
    if n < 30: return None, None
    returns = np.diff(price) / price[:-1]
    X, y = [], []
    for i in range(20, n - 3):
        past = [
            returns[i-1], returns[i-2], returns[i-3], returns[i-5],
            np.mean(returns[i-10:i]), np.std(returns[i-10:i]),
            np.mean(returns[i-5:i]),
            np.max(returns[i-5:i]),
            np.min(returns[i-5:i]),
            price[i] / np.mean(price[i-20:i]) - 1,  # فاصله از میانگین متحرک
        ]
        X.append(past)
        y.append(np.sign(returns[i+1]))
    return np.array(X), np.array(y)

def test_timeframe(name, file_path):
    print(f"\n" + "=" * 70)
    print(f"🔬 تایم‌فریم {name} (بعد ۴)")
    print("=" * 70)
    try:
        df = pd.read_csv(file_path)
        if 'close' in df.columns: price = df['close'].values
        elif 'Close' in df.columns: price = df['Close'].values
        else: price = df.iloc[:, 4].values
        price = np.array(price, dtype=float)
        price = price[np.isfinite(price)]
        print(f"📊 داده: {len(price)} کندل")
    except Exception as e:
        print(f"❌ خطا: {e}")
        return None
    
    X, y = build_dim4(price)
    if X is None or len(X) < 50:
        print(f"⚠️ داده کافی نیست")
        return None
    
    feature_names = ['r1', 'r2', 'r3', 'r5', 'mean10', 'std10', 'mean5', 'max5', 'min5', 'dist_ma20']
    split = int(len(X) * 0.7)
    X_tr, y_tr = X[:split], y[:split]
    X_te, y_te = X[split:], y[split:]
    print(f"📊 آموزش: {len(X_tr)} | تست: {len(X_te)}")
    
    y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
    y_norm = (y_tr - y_m) / y_s
    
    print(f"⏳ آموزش مدل...")
    np.random.seed(42)
    random.seed(42)
    try:
        tree, _, a = gp_core_v27(X_tr, y_norm, feature_names, generations=50, pop_size=300, max_nodes=15)
        if tree is None: return None
        
        pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, feature_names)) * a
        signals = np.sign(pred_te)
        actual = np.sign(y_te)
        mask = actual != 0
        
        if mask.sum() == 0: return None
        acc = np.mean(signals[mask] == actual[mask]) * 100
        
        emoji = "🏆" if acc > 95 else "🥇" if acc > 85 else "⚠️"
        print(f"\n  {emoji} دقت بعد ۴: {acc:.2f}%")
        print(f"  📊 تعداد سیگنال: {int(mask.sum())}")
        print(f"  📜 فرمول: {str(tree)[:80]}")
        return {'acc': acc, 'n_test': len(X_te), 'n_signals': int(mask.sum())}
    except Exception as e:
        print(f"❌ خطا: {e}")
        return None

results = {}
res_h4 = test_timeframe('H4 (4 ساعته)', 'data/EURUSD_h4.csv')
if res_h4: results['H4'] = res_h4
res_d1 = test_timeframe('D1 (روزانه)', 'data/EURUSD_d1.csv')
if res_d1: results['D1'] = res_d1

print("\n" + "=" * 70)
print("📊 مقایسه بعد ۱۶ و بعد ۴:")
print("=" * 70)
print(f"{'تایم‌فریم':<15} | {'دقت بعد ۱۶':<15} | {'دقت بعد ۴':<15}")
print("-" * 60)
for tf_name in results:
    acc16 = 100.0
    acc4 = results[tf_name]['acc']
    print(f"{tf_name:<15} | {acc16:>10.2f}%    | {acc4:>10.2f}%")
print("=" * 70)
