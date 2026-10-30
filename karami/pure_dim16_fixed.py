import numpy as np
import pandas as pd
import random
import warnings
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🌌 بعد ۱۶ خالص (اصلاح‌شده با ویژگی خنثی)")
print("=" * 70)

def load_data(path):
    df = pd.read_csv(path)
    for c in df.columns:
        if str(c).lower() == 'close':
            return df[c].values
    return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

price = load_data('data/EURUSD_h4.csv')
n = len(price)

# 🌟 آینده (بعد ۱۶)
fut_r1 = np.zeros(n)
fut_r1[:-1] = (price[1:] - price[:-1]) / price[:-1]

y_dir = np.zeros(n)
y_dir[:-1] = np.sign(price[1:] - price[:-1])

# 🛠️ اضافه کردن ویژگی خنثی (Dummy) برای جلوگیری از کرش موتور
dummy = np.zeros(n)

X = np.column_stack([fut_r1, dummy])
features = ['fut_r1', 'dummy']

valid = np.isfinite(X[:,0]) & np.isfinite(y_dir)
X, y_dir = X[valid], y_dir[valid]
n = len(X)
print(f"📊 داده: {n} کندل")

split = int(n * 0.6)
X_tr, y_tr = X[:split], y_dir[:split]
X_te, y_te = X[split:], y_dir[split:]

y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
y_norm = (y_tr - y_m) / y_s

print("⏳ آموزش مدل خالص بعد ۱۶...")
np.random.seed(42); random.seed(42)
tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=20, pop_size=150, max_nodes=5)

if tree is None: sys.exit()

pred_te = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
signals = np.sign(pred_te)
actual = np.sign(y_te)
mask = actual != 0

acc = np.mean(signals[mask] == actual[mask]) * 100
print("\n" + "=" * 70)
print(f"🏆 دقت مطلق با فقط fut_r1: {acc:.2f}%")
print(f"📜 فرمول: {str(tree)}")
print("=" * 70)
