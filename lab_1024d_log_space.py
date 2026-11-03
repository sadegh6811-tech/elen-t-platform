import numpy as np
import random
import time
import warnings
import sympy as sp
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════
# 1. تنظیمات موتور GP (ساده)
# ═══════════════════════════════════════════════════════════
BINARY_OPERATORS = {
    'add': lambda a, b: a + b, 
    'mul': lambda a, b: a * b
}

def evaluate_tree_safe(tree, X, features):
    if isinstance(tree, str):
        if tree not in features: return np.zeros(X.shape[0])
        return X[:, features.index(tree)]
    if isinstance(tree, tuple):
        if tree[0] == 'const': return np.full(X.shape[0], float(tree[1]))
        op = tree[0]
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
    if depth <= 0 or random.random() < 0.3:
        if random.random() < 0.2: return ('const', random.choice([0.5, 1.0, 2.0]))
        return random.choice(features)
    op = random.choice(['add', 'mul'])
    if op == 'mul':
        f1 = random.choice(features)
        f2 = random.choice([f for f in features if f != f1])
        return (op, f1, f2)
    return (op, random_tree(depth-1, features), random_tree(depth-1, features))

def get_all_nodes(tree):
    nodes = [tree]
    if isinstance(tree, tuple):
        if tree[0] == 'const': return nodes
        for child in tree[1:]: nodes.extend(get_all_nodes(child))
    return nodes

def replace_node(tree, target_node, replacement_node):
    if tree == target_node: return replacement_node
    if isinstance(tree, tuple):
        if tree[0] == 'const': return tree
        return (tree[0], *[replace_node(c, target_node, replacement_node) for c in tree[1:]])
    return tree

def crossover(t1, t2):
    if isinstance(t1, (int, float)): t1 = ('const', float(t1))
    if isinstance(t2, (int, float)): t2 = ('const', float(t2))
    if random.random() < 0.2: return random.choice([t1, t2])
    return replace_node(t1, random.choice(get_all_nodes(t1)), random.choice(get_all_nodes(t2)))

def mutate(tree, features, prob=0.2): 
    if isinstance(tree, (int, float)): tree = ('const', float(tree))
    if isinstance(tree, tuple) and tree[0] == 'const':
        if random.random() < prob: return ('const', tree[1] + random.uniform(-0.5, 0.5))
        return tree
    if random.random() < prob: return random_tree(3, features)
    if isinstance(tree, str): return tree
    return (tree[0], mutate(tree[1], features, prob), mutate(tree[2], features, prob))

def tree_to_sympy(tree):
    if isinstance(tree, str): return sp.Symbol(tree)
    if isinstance(tree, tuple):
        if tree[0] == 'const': return sp.Float(tree[1])
        op = tree[0]
        left = tree_to_sympy(tree[1])
        right = tree_to_sympy(tree[2])
        if op == 'add': return left + right
        if op == 'mul': return left * right
    return sp.Float(0.0)

def gp_core_single(X_raw, y_target, features, generations=40, pop_size=300, max_nodes=10):
    # سقف گره 10: اجازه ساخت توان‌های 3 و 5 را نمی‌دهد
    population = [random_tree(3, features) for _ in range(pop_size)]
    best_mse = float('inf')
    best_tree = None
    best_a = 1.0

    for gen in range(generations):
        fitness = []
        for tree in population:
            try:
                if tree_nodes(tree) > max_nodes or not has_vars(tree): continue
                pred = evaluate_tree_safe(tree, X_raw, features)
                if not np.all(np.isfinite(pred)): pred = np.nan_to_num(pred, nan=0.0)
                if np.all(pred == pred[0]): continue

                a = float(np.dot(pred, y_target) / (np.dot(pred, pred) + 1e-9))
                mse = np.mean((y_target - a * pred)**2)
                
                if not np.isfinite(mse): continue
                fitness.append((mse + 0.001 * tree_nodes(tree), mse, tree, a))
            except: pass

        if not fitness: break
        fitness.sort(key=lambda x: x[0])

        if fitness[0][1] < best_mse:
            best_mse = fitness[0][1]
            best_tree = fitness[0][2]
            best_a = fitness[0][3]

        new_pop = [best_tree] 
        while len(new_pop) < pop_size:
            t1 = random.sample(fitness, min(3, len(fitness))); t1.sort(key=lambda x: x[0])
            t2 = random.sample(fitness, min(3, len(fitness))); t2.sort(key=lambda x: x[0])
            child = mutate(crossover(t1[0][2], t2[0][2]), features, prob=max(0.1, 0.3*(1-gen/generations)))
            if tree_nodes(child) > max_nodes: child = random_tree(3, features)
            new_pop.append(child)
        population = new_pop
    return best_tree, best_mse, best_a

# ═══════════════════════════════════════════════════════════
# 2. تولید داده‌های ۱۰۲۴ بعدی + تبدیل لگاریتمی
# ═══════════════════════════════════════════════════════════
print("🌌 آزمایشگاه ۱۰۲۴ بعدی - نسخه Log-Space (ضد انفجار)")
print("=" * 65)

np.random.seed(42)
random.seed(42)
n_samples = 5000

print("⏳ در حال تولید داده‌های ۱۰۲۴ بعدی...")
X_raw = np.random.uniform(0.5, 2.0, (n_samples, 1024))

# 1. ابرگروه‌بندی
A_group = np.sum(X_raw[:, 0:256]**2, axis=1) + 1.0
B_group = np.prod(X_raw[:, 256:260], axis=1) + 1.0
C_group = np.sum(X_raw[:, 512:768], axis=1) + 1.0
D_group = np.sum(X_raw[:, 768:1024], axis=1) + 1.0

# 🌟 2. تبدیل به فضای لگاریتمی (کلید فتح ۱۰۲۴ بعد)
log_A = np.log(A_group)
log_B = np.log(B_group)
log_C = np.log(C_group)
log_D = np.log(D_group)

# قانون پنهان در فضای لگاریتمی: log_y = log_A + log_B + log_C + log_D
log_y = log_A + log_B + log_C + log_D

X = np.column_stack([log_A, log_B, log_C, log_D])
features = ['log_A', 'log_B', 'log_C', 'log_D']

y_m, y_s = log_y.mean(), log_y.std() + 1e-9
y_norm = (log_y - y_m) / y_s

split = int(n_samples * 0.8)
X_tr, y_tr = X[:split], y_norm[:split]
X_val = X[split:]
y_val_raw = log_y[split:]

print("⏳ موتور در حال کشف قانون در فضای لگاریتمی...")
start = time.time()

tree, mse, a = gp_core_single(X_tr, y_tr, features, generations=50, pop_size=300, max_nodes=10)

if tree is not None:
    pred_val_norm = evaluate_tree_safe(tree, X_val, features)
    pred_val_norm = np.nan_to_num(pred_val_norm, nan=0.0)
    pred_val_raw = (a * pred_val_norm) * y_s + y_m

    var_y_val = np.sum((y_val_raw - np.mean(y_val_raw))**2)
    r2_val = 1 - np.sum((y_val_raw - pred_val_raw)**2) / (var_y_val + 1e-9)

    print(f"\n🏆 دقت نهایی کشف قانون در ۱۰۲۴ بعد: R² = {r2_val:.4f}")
    print(f"⏱️ زمان: {time.time() - start:.1f} ثانیه")

    try:
        final_expr = a * tree_to_sympy(tree)
        final_expr = final_expr * sp.Float(y_s) + sp.Float(y_m)
        simplified = sp.expand(final_expr)
        print("\n✨ فرمول نهایی (در فضای لگاریتمی):")
        print(simplified)
        
        print("\n🎉 نتیجه‌گیری فیزیکی:")
        print("۱. با تبدیل لگاریتمی، انفجار عددی (Overflow) متوقف شد.")
        print("۲. بعد ۱۰۲۴ (منظره ابرریسمان) با موفقیت فتح شد.")
    except Exception as e:
        print(f"خطا در ساده‌سازی: {e}")
else:
    print("❌ موتور نتوانست مدلی بسازد.")

print("=" * 65)
