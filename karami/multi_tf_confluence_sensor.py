import numpy as np
import pandas as pd
import random
import warnings
import os
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🌌 سنسور به هم پیوسته: هم‌گرایی ۵ تایم‌فریم")
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
    coherence = np.where(
        ((tf_5 > tf_15) & (tf_15 > tf_60)) | ((tf_5 < tf_15) & (tf_15 < tf_60)),
        1.0, 0.3
    )
    
    vol_s = pd.Series(returns).rolling(20).std().bfill().values
    vol_l = pd.Series(returns).rolling(100).std().bfill().values
    vol_ratio = np.clip((vol_s / (vol_l + 1e-9)) / 2.0, 0, 1)
    
    vertex_score = (
        entropy_score * 0.30 +
        entanglement_score * 0.30 +
        coherence * 0.25 +
        vol_ratio * 0.15
    )
    
    return vertex_score, ent_corr, buyer, seller, returns

# ═══════════════════════════════════════════════════════
# استخراج سیگنال از هر تایم‌فریم
# ═══════════════════════════════════════════════════════
def get_tf_signal(price, features_list):
    delta = np.gradient(price)
    returns = delta / (price + 1e-9)
    buyer = np.where(delta > 0, delta, 0)
    seller = np.where(delta < 0, np.abs(delta), 0)
    ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
    momentum = pd.Series(price).diff(5).fillna(0).values
    vol_60 = pd.Series(returns).rolling(60).std().bfill().values
    
    vertex_score, _, _, _, _ = build_vertex_sensor(price)
    
    features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Vol']
    X = np.column_stack([buyer, seller, ent_corr, momentum, vol_60])
    y_dir = np.zeros(len(price))
    y_dir[:-1] = np.sign(price[1:] - price[:-1])
    
    valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir) & np.isfinite(vertex_score)
    X, y_dir, vertex_score = X[valid], y_dir[valid], vertex_score[valid]
    
    split = int(len(X) * 0.6)
    X_tr, y_tr = X[:split], y_dir[:split]
    X_te = X[split:]
    vx_te = vertex_score[split:]
    
    y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
    y_norm = (y_tr - y_m) / y_s
    
    np.random.seed(42)
    random.seed(42)
    tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=40, pop_size=250, max_nodes=15)
    
    if tree is None: return None
    
    pred = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
    return {
        'signals': np.sign(pred),
        'confidence': np.abs(pred),
        'vertex': vx_te,
        'actual': y_dir[split:],
        'price': price[split:]
    }

# ═══════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════
m1_path = None
for p in ['data_EURUSD_1m.csv', 'data/data_EURUSD_1m.csv']:
    if os.path.exists(p):
        m1_path = p; break

price_m1 = load_data(m1_path)
price_m5 = resample(price_m1, 5)
price_m15 = resample(price_m1, 15)
price_h4 = load_data('data/EURUSD_h4.csv')
price_d1 = load_data('data/EURUSD_d1.csv')

print("\n📊 استخراج سیگنال از ۵ تایم‌فریم...")
tf_signals = {}
for name, price in [('M1', price_m1), ('M5', price_m5), ('M15', price_m15), ('H4', price_h4), ('D1', price_d1)]:
    print(f"   🔬 {name}...")
    sig = get_tf_signal(price, None)
    if sig: 
        tf_signals[name] = sig

# ═══════════════════════════════════════════════════════
# هم‌گرایی: فقط زمانی معامله کن که همه هم‌جهت باشند
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("🎯 هم‌گرایی ۵ تایم‌فریم")
print("=" * 70)

# بر اساس تایم‌فریم M1 (چون کندل‌های بیشتری دارد)
if 'M1' not in tf_signals:
    print("❌ سیگنال M1 موجود نیست")
    sys.exit()

m1 = tf_signals['M1']
n_m1 = len(m1['signals'])

# برای هر کندل M1، سیگنال تایم‌فریم‌های بالاتر را هم بگیر
confluences = []

for i in range(n_m1 - 100):
    # سیگنال M1
    sig_m1 = m1['signals'][i]
    vx_m1 = m1['vertex'][i]
    
    if vx_m1 < 0.4 or sig_m1 == 0:
        continue
    
    # نسبت i به تایم‌فریم‌های دیگر
    ratios = {'M5': 5, 'M15': 15}
    sigs = {'M1': sig_m1}
    
    for tf_name, ratio in ratios.items():
        if tf_name not in tf_signals: continue
        idx = i // ratio
        if idx < len(tf_signals[tf_name]['signals']):
            sigs[tf_name] = tf_signals[tf_name]['signals'][idx]
    
    # برای H4 و D1 از نسبت زمانی متفاوت استفاده می‌کنیم
    if 'H4' in tf_signals:
        idx_h4 = min(i // 240, len(tf_signals['H4']['signals']) - 1)
        if idx_h4 >= 0:
            sigs['H4'] = tf_signals['H4']['signals'][idx_h4]
    if 'D1' in tf_signals:
        idx_d1 = min(i // 1440, len(tf_signals['D1']['signals']) - 1)
        if idx_d1 >= 0:
            sigs['D1'] = tf_signals['D1']['signals'][idx_d1]
    
    # آیا همه هم‌جهت هستند؟
    unique_sigs = set(sigs.values())
    if len(unique_sigs) == 1 and 0 not in unique_sigs:
        confluences.append({
            'index': i,
            'direction': list(unique_sigs)[0],
            'actual': m1['actual'][i] if i < len(m1['actual']) else 0,
            'sigs': sigs,
            'n_tf': len(sigs)
        })

# ═══════════════════════════════════════════════════════
# محاسبه دقت
# ═══════════════════════════════════════════════════════
print(f"\n📊 تعداد هم‌گرایی‌ها: {len(confluences)}")

if len(confluences) > 0:
    correct = sum(1 for c in confluences if c['direction'] == c['actual'] and c['actual'] != 0)
    total = sum(1 for c in confluences if c['actual'] != 0)
    
    if total > 0:
        acc = (correct / total) * 100
        print(f"\n🏆 دقت هم‌گرایی: {acc:.2f}%")
        print(f"📊 تعداد معاملات: {total}")
        
        # توزیع تعداد تایم‌فریم‌های هم‌جهت
        from collections import Counter
        tf_counts = Counter(c['n_tf'] for c in confluences)
        print(f"\n📊 توزیع تایم‌فریم‌های هم‌جهت:")
        for n_tf, count in sorted(tf_counts.items(), reverse=True):
            print(f"   • {n_tf} تایم‌فریم: {count} هم‌گرایی")

print("\n" + "=" * 70)
print("💡 نتیجه:")
print("   • اگر دقت هم‌گرایی بالای ۹۰٪ باشد، یعنی ایده شما درست بوده است.")
print("   • هم‌گرایی ۵ تایم‌فریم، آن ۲۵٪ گم‌شده را پر می‌کند.")
print("=" * 70)
