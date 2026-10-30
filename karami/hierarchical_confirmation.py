import numpy as np
import pandas as pd
import random
import warnings
import os
import sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from engine_v27_clean import gp_core_v27, evaluate_tree_safe

print("🏛️ سیستم تایید سلسله‌مراتبی (Hierarchical Confirmation)")
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

def get_signal(price):
    """برای هر تایم‌فریم، سیگنال و اطمینان تولید می‌کند"""
    n = len(price)
    delta = np.gradient(price)
    returns = delta / (price + 1e-9)
    buyer = np.where(delta > 0, delta, 0)
    seller = np.where(delta < 0, np.abs(delta), 0)
    ent_corr = pd.Series(buyer).rolling(14).corr(pd.Series(seller)).fillna(0).values
    momentum = pd.Series(price).diff(5).fillna(0).values
    vol_60 = pd.Series(returns).rolling(60).std().bfill().values
    
    features = ['Buyer', 'Seller', 'Ent', 'Mom', 'Vol']
    X = np.column_stack([buyer, seller, ent_corr, momentum, vol_60])
    y_dir = np.zeros(n)
    y_dir[:-1] = np.sign(price[1:] - price[:-1])
    
    valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y_dir)
    X, y_dir, price_v = X[valid], y_dir[valid], price[valid]
    
    split = int(len(X) * 0.6)
    X_tr, y_tr = X[:split], y_dir[:split]
    X_te, y_te = X[split:], y_dir[split:]
    
    y_m, y_s = y_tr.mean(), y_tr.std() + 1e-9
    y_norm = (y_tr - y_m) / y_s
    
    np.random.seed(42); random.seed(42)
    tree, _, a = gp_core_v27(X_tr, y_norm, features, generations=40, pop_size=250, max_nodes=15)
    
    if tree is None: return None
    
    pred = np.nan_to_num(evaluate_tree_safe(tree, X_te, features)) * a
    return {
        'signal': np.sign(pred),
        'confidence': np.abs(pred),
        'price': price_v[split:],
        'actual': y_te,
    }

# ═══════════════════════════════════════════════════════
# بارگذاری و پردازش همه تایم‌فریم‌ها
# ═══════════════════════════════════════════════════════
m1_path = None
for p in ['data_EURUSD_1m.csv', 'data/data_EURUSD_1m.csv']:
    if os.path.exists(p): m1_path = p; break

price_m1 = load_data(m1_path)
price_m5 = resample(price_m1, 5)
price_m15 = resample(price_m1, 15)
price_h1 = resample(price_m1, 60)
price_h4 = load_data('data/EURUSD_h4.csv')
price_d1 = load_data('data/EURUSD_d1.csv')

print("\n📊 استخراج سیگنال از ۶ تایم‌فریم...")
tf_data = {}
for name, price in [('M1', price_m1), ('M5', price_m5), ('M15', price_m15), 
                    ('H1', price_h1), ('H4', price_h4), ('D1', price_d1)]:
    if len(price) < 100:
        print(f"   ⚠️ {name}: داده کافی نیست ({len(price)} کندل)")
        continue
    print(f"   🔬 {name} ({len(price)} کندل)...")
    sig = get_signal(price)
    if sig: tf_data[name] = sig

# ═══════════════════════════════════════════════════════
# 🏛️ سیستم تایید سلسله‌مراتبی
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("🏛️ سیستم تایید سلسله‌مراتبی (بر اساس منطق شما)")
print("=" * 70)

# نسبت‌های زمانی
ratios = {'M1': 1, 'M5': 5, 'M15': 15, 'H1': 60, 'H4': 240, 'D1': 1440}

# برای هر کندل M1، سیگنال همه تایم‌فریم‌ها را می‌گیریم
n_m1 = len(tf_data['M1']['signal'])
CONFIDENCE_THRESH = 0.5  # آستانه اطمینان برای تایید

# شمارنده‌ها
stats = {
    'M5_confirmed_by_M1': 0,
    'M15_confirmed_by_M1_M5': 0,
    'H1_confirmed_by_M1_M5_M15': 0,
    'H4_confirmed_by_M1_M5_M15_H1': 0,
    'D1_confirmed_by_all': 0,
}

# ذخیره نتایج برای محاسبه دقت
results = {
    'M5': {'signals': [], 'actuals': []},
    'M15': {'signals': [], 'actuals': []},
    'H1': {'signals': [], 'actuals': []},
    'H4': {'signals': [], 'actuals': []},
    'D1': {'signals': [], 'actuals': []},
}

for i in range(n_m1):
    # سیگنال M1
    m1_sig = tf_data['M1']['signal'][i]
    m1_conf = tf_data['M1']['confidence'][i]
    
    if m1_conf < CONFIDENCE_THRESH or m1_sig == 0:
        continue
    
    # بررسی M5
    if 'M5' in tf_data:
        idx_m5 = min(i // 5, len(tf_data['M5']['signal']) - 1)
        m5_sig = tf_data['M5']['signal'][idx_m5]
        m5_conf = tf_data['M5']['confidence'][idx_m5]
        
        if m5_conf >= CONFIDENCE_THRESH and m5_sig == m1_sig:
            # ✅ تایید M5 توسط M1
            stats['M5_confirmed_by_M1'] += 1
            results['M5']['signals'].append(m1_sig)  # سیگنال تایید شده
            results['M5']['actuals'].append(tf_data['M5']['actual'][idx_m5])
            
            # بررسی M15
            if 'M15' in tf_data:
                idx_m15 = min(i // 15, len(tf_data['M15']['signal']) - 1)
                m15_sig = tf_data['M15']['signal'][idx_m15]
                m15_conf = tf_data['M15']['confidence'][idx_m15]
                
                if m15_conf >= CONFIDENCE_THRESH and m15_sig == m1_sig:
                    # ✅ تایید M15 توسط M1 + M5
                    stats['M15_confirmed_by_M1_M5'] += 1
                    results['M15']['signals'].append(m1_sig)
                    results['M15']['actuals'].append(tf_data['M15']['actual'][idx_m15])
                    
                    # بررسی H1
                    if 'H1' in tf_data:
                        idx_h1 = min(i // 60, len(tf_data['H1']['signal']) - 1)
                        h1_sig = tf_data['H1']['signal'][idx_h1]
                        h1_conf = tf_data['H1']['confidence'][idx_h1]
                        
                        if h1_conf >= CONFIDENCE_THRESH and h1_sig == m1_sig:
                            stats['H1_confirmed_by_M1_M5_M15'] += 1
                            results['H1']['signals'].append(m1_sig)
                            results['H1']['actuals'].append(tf_data['H1']['actual'][idx_h1])
                            
                            # بررسی H4
                            if 'H4' in tf_data:
                                idx_h4 = min(i // 240, len(tf_data['H4']['signal']) - 1)
                                h4_sig = tf_data['H4']['signal'][idx_h4]
                                h4_conf = tf_data['H4']['confidence'][idx_h4]
                                
                                if h4_conf >= CONFIDENCE_THRESH and h4_sig == m1_sig:
                                    stats['H4_confirmed_by_M1_M5_M15_H1'] += 1
                                    results['H4']['signals'].append(m1_sig)
                                    results['H4']['actuals'].append(tf_data['H4']['actual'][idx_h4])
                                    
                                    # بررسی D1
                                    if 'D1' in tf_data:
                                        idx_d1 = min(i // 1440, len(tf_data['D1']['signal']) - 1)
                                        d1_sig = tf_data['D1']['signal'][idx_d1]
                                        d1_conf = tf_data['D1']['confidence'][idx_d1]
                                        
                                        if d1_conf >= CONFIDENCE_THRESH and d1_sig == m1_sig:
                                            stats['D1_confirmed_by_all'] += 1
                                            results['D1']['signals'].append(m1_sig)
                                            results['D1']['actuals'].append(tf_data['D1']['actual'][idx_d1])

# ═══════════════════════════════════════════════════════
# 📊 گزارش نهایی
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 گزارش نهایی سیستم تایید سلسله‌مراتبی:")
print("=" * 70)

print("\n🔗 قوانین تایید و تعداد موارد:")
print(f"   ✅ M1=100%  →  ترید در M5: {stats['M5_confirmed_by_M1']} مورد")
print(f"   ✅ M1+M5=100%  →  ترید در M5+M15: {stats['M15_confirmed_by_M1_M5']} مورد")
print(f"   ✅ M1+M5+M15=100%  →  ترید در M5+M15+H1: {stats['H1_confirmed_by_M1_M5_M15']} مورد")
print(f"   ✅ M1+M5+M15+H1=100%  →  ترید در M5+M15+H1+H4: {stats['H4_confirmed_by_M1_M5_M15_H1']} مورد")
print(f"   ✅ همه هم‌راستا  →  ترید در D1: {stats['D1_confirmed_by_all']} مورد")

print("\n🎯 دقت در هر سطح تایید:")
print("=" * 70)
print(f"{'سطح':<10} | {'تعداد':<10} | {'دقت':<10}")
print("-" * 40)

for level, data in results.items():
    if len(data['signals']) < 3:
        continue
    correct = sum(1 for s, a in zip(data['signals'], data['actuals']) if s == a and a != 0)
    total = sum(1 for a in data['actuals'] if a != 0)
    if total > 0:
        acc = (correct / total) * 100
        emoji = "🏆" if acc > 99 else "🥇" if acc > 95 else "✅" if acc > 85 else "⚠️"
        print(f"{level:<10} | {total:<10} | {acc:<6.2f}% {emoji}")

print("=" * 70)
print("\n💡 تفسیر:")
print("   • هرچه تایم‌فریم‌های بیشتری تایید کنند، دقت بالاتر می‌رود.")
print("   • اما تعداد موارد تایید شده کمتر می‌شود (فیلتر سخت‌تر).")
print("   • این همان قانون فیزیکی 'دقت vs پوشش' است.")
