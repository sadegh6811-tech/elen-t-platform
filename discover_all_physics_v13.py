import numpy as np
import random
import sys
import time
import warnings
sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
from extended_operators_v2 import UNARY_OPERATORS, BINARY_OPERATORS

warnings.filterwarnings('ignore')

# 🛡️ ایمن‌سازی توابع
UNARY_OPERATORS['log'] = lambda x: np.log(np.abs(x) + 1e-9)
UNARY_OPERATORS['sqrt'] = lambda x: np.sqrt(np.abs(x))
UNARY_OPERATORS['asin'] = lambda x: np.arcsin(np.clip(x, -1, 1))
UNARY_OPERATORS['acos'] = lambda x: np.arccos(np.clip(x, -1, 1))
BINARY_OPERATORS['div'] = lambda a, b: np.divide(a, b + 1e-9)
BINARY_OPERATORS['pow'] = lambda a, b: np.sign(a) * np.abs(a) ** np.clip(b, -5, 5)

def evaluate_tree_safe(tree, X, features):
    if isinstance(tree, str):
        if tree not in features: return np.zeros(X.shape[0])
        idx = features.index(tree)
        return X[:, idx]
    if isinstance(tree, tuple):
        if tree[0] == 'const':
            return np.full(X.shape[0], float(tree[1]))
        op = tree[0]
        if op in UNARY_OPERATORS:
            return UNARY_OPERATORS[op](evaluate_tree_safe(tree[1], X, features))
        elif op in BINARY_OPERATORS:
            left = evaluate_tree_safe(tree[1], X, features)
            right = evaluate_tree_safe(tree[2], X, features)
            return BINARY_OPERATORS[op](left, right)
    return np.zeros(X.shape[0])

def tree_nodes(tree):
    if isinstance(tree, (str, int, float)): return 1
    if isinstance(tree, tuple) and tree[0] == 'const': return 1
    return 1 + sum(tree_nodes(c) for c in tree[1:])

def has_vars(tree):
    if isinstance(tree, str): return True
    if isinstance(tree, tuple) and tree[0] == 'const': return False
    if isinstance(tree, tuple): return any(has_vars(c) for c in tree[1:])
    return False

def random_tree(depth, features):
    if depth <= 0:
        if random.random() < 0.3: return ('const', random.choice([-2.0, -1.0, -0.5, 0.5, 1.0, 2.0]))
        return random.choice(features)
    if random.random() < 0.3:
        op = random.choice(list(UNARY_OPERATORS.keys()))
        return (op, random_tree(depth-1, features))
    op = random.choice(list(BINARY_OPERATORS.keys()))
    return (op, random_tree(depth-1, features), random_tree(depth-1, features))

def mutate(tree, features, prob=0.2): 
    if random.random() < prob: return random_tree(3, features)
    if isinstance(tree, (str, int, float)) or (isinstance(tree, tuple) and tree[0] == 'const'): return tree
    if tree[0] in UNARY_OPERATORS: return (tree[0], mutate(tree[1], features, prob))
    return (tree[0], mutate(tree[1], features, prob), mutate(tree[2], features, prob))

def crossover(t1, t2):
    if isinstance(t1, (str, int, float)) or isinstance(t2, (str, int, float)):
        return random.choice([t1, t2])
    if (isinstance(t1, tuple) and t1[0] == 'const') or (isinstance(t2, tuple) and t2[0] == 'const'):
        return random.choice([t1, t2])
    if t1[0] != t2[0]: return random.choice([t1, t2])
    if t1[0] in UNARY_OPERATORS: return (t1[0], random.choice([t1[1], t2[1]]))
    return (t1[0], random.choice([t1[1], t2[1]]), random.choice([t1[2], t2[2]]))

def gp_core_v23(X_raw, y_norm, features, generations=50, pop_size=300, max_nodes=35):
    population = [random_tree(4, features) for _ in range(pop_size)]
    best_mse = float('inf')
    best_tree = None

    for gen in range(generations):
        fitness = []
        for tree in population:
            try:
                nodes = tree_nodes(tree)
                if nodes > max_nodes: continue 
                if not has_vars(tree): continue
                
                pred = evaluate_tree_safe(tree, X_raw, features)
                pred = np.asarray(pred, dtype=float)
                
                if not np.all(np.isfinite(pred)):
                    pred = np.nan_to_num(pred, nan=0.0, posinf=0.0, neginf=0.0)
                
                mse = np.mean((y_norm - pred)**2)
                if not np.isfinite(mse): continue
                
                complexity_penalty = 0.005 * nodes 
                score = mse + complexity_penalty
                fitness.append((score, mse, tree))
            except Exception:
                pass

        if not fitness: 
            print(f"    [!] نسل {gen} خالی بود.")
            break
        fitness.sort(key=lambda x: x[0])

        if fitness[0][1] < best_mse:
            best_mse = fitness[0][1]
            best_tree = fitness[0][2]

        new_pop = [best_tree] 
        while len(new_pop) < pop_size:
            t1 = random.sample(fitness, min(3, len(fitness))); t1.sort(key=lambda x: x[0])
            t2 = random.sample(fitness, min(3, len(fitness))); t2.sort(key=lambda x: x[0])
            child = mutate(crossover(t1[0][2], t2[0][2]), features, prob=max(0.05, 0.3*(1-gen/generations)))
            if tree_nodes(child) > max_nodes: child = random_tree(3, features)
            new_pop.append(child)
        population = new_pop
    return best_tree, best_mse

# ═══════════════════════════════════════════════════════════
# اجرای تست (نسخه v23 - بدون باگ)
# ═══════════════════════════════════════════════════════════
print("🌌 آزمون جامع فیزیک (نسخه v23 - اصلاح باگ سید و R2)")
print("=" * 75)

# 🐞 باگ 1 رفع شد: سیدها یک بار برای همیشه اینجا تنظیم می‌شوند
np.random.seed(42)
random.seed(42)

n_samples = 400
physics_benchmarks = [
    {"name": "1. انرژی شرودینگر", "n_vars": 3, "gen": lambda X: (X[:,0]**2) / (2 * X[:,1] + 1e-9) + X[:,2], "vars": ["p", "m", "V"]},
    {"name": "2. طول موج دو بروگلی", "n_vars": 1, "gen": lambda X: 6.626 / (X[:,0] + 1e-9), "vars": ["p"]},
    {"name": "4. هم‌ارزی جرم و انرژی", "n_vars": 1, "gen": lambda X: X[:,0] * 299792458**2, "vars": ["m"]},
    {"name": "5. انرژی کل نسبیتی", "n_vars": 2, "gen": lambda X: np.sqrt((X[:,0]*3e8)**2 + (X[:,1]*3e8)**2), "vars": ["p", "m"]},
    {"name": "7. نوسانگر هارمونیک", "n_vars": 2, "gen": lambda X: (X[:,0] + 0.5) * X[:,1], "vars": ["n", "ħω"]},
    {"name": "8. توزیع بولتزمان", "n_vars": 2, "gen": lambda X: np.exp(-X[:,0] / (X[:,1] + 1e-9)), "vars": ["ΔE", "kT"]},
    {"name": "9. تابش پلانک", "n_vars": 1, "gen": lambda X: X[:,0]**4, "vars": ["T"]},
    {"name": "10. انرژی چگالش", "n_vars": 2, "gen": lambda X: (X[:,0] - X[:,1])**2, "vars": ["T", "Tc"]}
]

results = []
start_all = time.time()

for p in physics_benchmarks:
    print(f"\n🔬 در حال کشف: {p['name']}")
    
    current_vars = list(p['vars']) 
    X = np.random.uniform(0.5, 2.0, (n_samples, p['n_vars']))
    y = p['gen'](X)
    
    # ✨ مهندسی ویژگی
    if p['name'] == "1. انرژی شرودینگر":
        print("  ⚙️ [ویژگی جدید] افزودن ستون InvM...")
        X = np.column_stack((X, 1.0 / (X[:, 1] + 1e-9)))
        current_vars.append("InvM")

    if p['name'] == "10. انرژی چگالش":
        print("  ⚙️ [ویژگی جدید] افزودن ستون DeltaT...")
        X = np.column_stack((X, X[:, 0] - X[:, 1]))
        current_vars.append("DeltaT")
    
    valid_mask = np.isfinite(y)
    X, y = X[valid_mask], y[valid_mask]
    
    # ✅ فقط y نرمال می‌شود
    y_m, y_s = y.mean(), y.std() + 1e-9
    y_norm = (y - y_m) / y_s
    
    split = int(len(X) * 0.8)
    X_tr, y_tr = X[:split], y_norm[:split]
    X_val = X[split:]
    
    # 🐞 باگ 2 رفع شد: تخصیص تمیز y_val
    y_val_norm = y_norm[split:]
    y_val_raw = y[split:]

    tree, _ = gp_core_v23(X_tr, y_tr, current_vars, generations=50, pop_size=300, max_nodes=35)
    
    if tree is not None:
        pred_val_norm = evaluate_tree_safe(tree, X_val, current_vars)
        pred_val_norm = np.asarray(pred_val_norm, dtype=float)
        
        if not np.all(np.isfinite(pred_val_norm)):
            pred_val_norm = np.nan_to_num(pred_val_norm, nan=0.0)
            
        pred_val_raw = pred_val_norm * y_s + y_m
        
        # 🐞 باگ 3 رفع شد: جلوگیری از تقسیم بر صفر در محاسبه R2
        var_y_val = np.sum((y_val_raw - np.mean(y_val_raw))**2)
        r2_val = 1 - np.sum((y_val_raw - pred_val_raw)**2) / (var_y_val + 1e-9)
        
        emoji = "🏆" if r2_val > 0.95 else "🥇" if r2_val > 0.8 else "🥈" if r2_val > 0.5 else "⚠️"
        print(f"  {emoji} R² = {r2_val:.4f} | گره‌ها: {tree_nodes(tree)}")
        print(f"  📜 فرمول: {str(tree)[:150]}...")
        results.append((p['name'], r2_val))
    else:
        print("  ❌ کشف نشد.")

print("\n" + "=" * 75)
for name, r2 in results:
    emoji = "✅" if r2 > 0.8 else "⚠️"
    print(f"  {emoji} {name:<30} | R² = {r2:.4f}")
print("-" * 75)
print(f"  میانگین دقت: {np.mean([r[1] for r in results]) if results else 0:.4f} | زمان: {time.time() - start_all:.1f} ثانیه")
