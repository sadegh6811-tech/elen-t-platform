import numpy as np
import pandas as pd
import random
import warnings
import os
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🌌 سنسور جامع (اصلاح‌شده): بک‌تست واقعی در M1")
print("=" * 70)

def load_data(path):
    df = pd.read_csv(path)
    for c in df.columns:
        if str(c).lower() == 'close':
            return df[c].values
    return pd.to_numeric(df.iloc[:, 4], errors='coerce').dropna().values

def resample(price_1m, minutes):
    n = len(price_1m) // minutes * minutes
    if n < minutes * 100: return np.array([])
    return price_1m[:n].reshape(-1, minutes)[:, -1]

def build_vertex_sensor(price):
    n = len(price)
    delta = np.gradient(price)
    returns = delta / (price + 1e-9)
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
    entropy = shannon_entropy(returns)
    entropy_score = 1 - np.clip(entropy / np.log2(10), 0, 1)
    buyer = np.where(delta > 0, delta, 0)
    seller = np.where(delta < 0, np.abs(delta), 0)
    ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
    entanglement_score = np.abs(ent_corr)
    tf_5 = pd.Series(price).rolling(5).mean().bfill().values
    tf_15 = pd.Series(price).rolling(15).mean().bfill().values
    tf_60 = pd.Series(price).rolling(60).mean().bfill().values
    coherence = np.where(((tf_5 > tf_15) & (tf_15 > tf_60)) | ((tf_5 < tf_15) & (tf_15 < tf_60)), 1.0, 0.3)
    vol_s = pd.Series(returns).rolling(20).std().bfill().values
    vol_l = pd.Series(returns).rolling(100).std().bfill().values
    vol_ratio = np.clip((vol_s / (vol_l + 1e-9)) / 2.0, 0, 1)
    return entropy_score * 0.30 + entanglement_score * 0.30 + coherence * 0.25 + vol_ratio * 0.15

def get_tf_signal(price):
    delta = np.gradient(price)
    returns = delta / (price + 1e-9)
    buyer = np.where(delta > 0, delta, 0)
    seller = np.where(delta < 0, np.abs(delta), 0)
    ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
    momentum = pd.Series(price).diff(5).fillna(0).values
    vol_60 = pd.Series(returns).rolling(60).std().bfill().values
    vertex_score = build_vertex_sensor(price)
    features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Vol']
    X = np.column_stack([buyer, seller, ent_corr, momentum, vol_60])
    y_dir = np.zeros(len(price))
    y_dir[:-1] = np.sign(price[1:] - price[:-1])
    valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir) & np.isfinite(vertex_score)
    X, y_dir, vertex_score, price_valid = X[valid], y_dir[valid], vertex_score[valid], price[valid]
    split = int(len(X) * 0.6)
    X_tr, y_tr = X[:split], y_dir[:split]
    X_te = X[split:]
    vx_te = vertex_score[split:]
    y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
    y_norm = (y_tr - y_m) / y_s
    np.random.seed(42); random.seed(42)
    tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=40, pop_size=250, max_nodes=15)
    if tree is None: return None
    pred = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
    return {'raw_pred': pred, 'signals': np.sign(pred), 'confidence': np.abs(pred), 'vertex': vx_te, 'price': price_valid[split:], 'actual': y_dir[split:]}

# ═══════════════════════════════════════════════════════
m1_path = None
for p in ['data_EURUSD_1m.csv', 'data/data_EURUSD_1m.csv']:
    if os.path.exists(p): m1_path = p; break

price_m1 = load_data(m1_path)
price_m5 = resample(price_m1, 5)
price_m15 = resample(price_m1, 15)
price_h4 = load_data('data/EURUSD_h4.csv')
price_d1 = load_data('data/EURUSD_d1.csv')

print("\n📊 استخراج سیگنال...")
tf_signals = {}
for name, price in [('M1', price_m1), ('M5', price_m5), ('M15', price_m15), ('H4', price_h4), ('D1', price_d1)]:
    sig = get_tf_signal(price)
    if sig: tf_signals[name] = sig

# ═══════════════════════════════════════════════════════
# 🌟 سنسور جامع
# ═══════════════════════════════════════════════════════
m1 = tf_signals['M1']
n_m1 = len(m1['raw_pred'])
weights = {'M1': 0.10, 'M5': 0.15, 'M15': 0.20, 'H4': 0.25, 'D1': 0.30}

master_signals = np.zeros(n_m1)
master_confidence = np.zeros(n_m1)
master_actual = np.zeros(n_m1)

for i in range(n_m1):
    combined_signal = 0; combined_conf = 0; total_weight = 0
    combined_signal += m1['raw_pred'][i] * weights['M1']; combined_conf += m1['confidence'][i] * weights['M1']; total_weight += weights['M1']
    for tf_name, ratio in [('M5', 5), ('M15', 15)]:
        if tf_name in tf_signals:
            idx = i // ratio
            if idx < len(tf_signals[tf_name]['raw_pred']):
                combined_signal += tf_signals[tf_name]['raw_pred'][idx] * weights[tf_name]
                combined_conf += tf_signals[tf_name]['confidence'][idx] * weights[tf_name]
                total_weight += weights[tf_name]
    for tf_name, ratio in [('H4', 240), ('D1', 1440)]:
        if tf_name in tf_signals:
            idx = min(i // ratio, len(tf_signals[tf_name]['raw_pred']) - 1)
            if idx >= 0:
                combined_signal += tf_signals[tf_name]['raw_pred'][idx] * weights[tf_name]
                combined_conf += tf_signals[tf_name]['confidence'][idx] * weights[tf_name]
                total_weight += weights[tf_name]
    if total_weight > 0:
        master_signals[i] = combined_signal / total_weight
        master_confidence[i] = combined_conf / total_weight
    master_actual[i] = m1['actual'][i]

# ═══════════════════════════════════════════════════════
# 💰 بک‌تست (اصلاح SL/TP برای M1)
# ═══════════════════════════════════════════════════════
print("\n💰 بک‌تست سودآوری سنسور جامع (SL/TP مناسب M1)...")
print("=" * 70)

initial_balance = 1000
balance = initial_balance
risk_amount = 10
tp_pips = 0.0020  # 🛠️ 20 پیپ سود (مناسب M1)
sl_pips = 0.0010  # 🛠️ 10 پیپ ضرر
optimal_thresh = 0.5

price_m1_te = m1['price']
trade_count = 0; win_count = 0; last_idx = -10

for i in range(n_m1 - 20):
    if i - last_idx < 5: continue
    if master_confidence[i] < optimal_thresh: continue
    if master_signals[i] == 0: continue
    if master_actual[i] == 0: continue
    
    direction = np.sign(master_signals[i])
    entry = price_m1_te[i]
    
    result = None
    for j in range(1, 20):
        if i+j >= len(price_m1_te): break
        move = (price_m1_te[i+j] - entry) * direction
        if move >= tp_pips:
            result = 'win'; pnl = risk_amount * (tp_pips / sl_pips); break
        elif move <= -sl_pips:
            result = 'loss'; pnl = -risk_amount; break
    
    if result is None: continue
    
    balance += pnl
    trade_count += 1
    if result == 'win': win_count += 1
    last_idx = i

print(f"\n📊 گزارش نهایی (آستانه {optimal_thresh}):")
print(f"  💰 موجودی اولیه: ${initial_balance:.2f}")
print(f"  📈 تعداد معاملات: {trade_count}")
print(f"  ✅ برد: {win_count} | ❌ باخت: {trade_count - win_count}")
if trade_count > 0:
    print(f"  🎯 دقت معاملات: {(win_count/trade_count)*100:.2f}%")
print(f"  💵 موجودی نهایی: ${balance:.2f}")
print(f"  📈 سود خالص: {((balance - initial_balance) / initial_balance * 100):+.2f}%")
print("=" * 70)
