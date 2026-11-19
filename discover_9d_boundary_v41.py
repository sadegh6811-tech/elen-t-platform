import random
import numpy as np
import sympy as sp
import time

# 🟢 خاموش کردن هشدارهای NumPy برای تقسیم بر صفر و مقادیر نامعتبر در طول جستجو
np.seterr(divide='ignore', invalid='ignore', over='ignore')

# Define binary operators for the GP
BINARY_OPERATORS = {
    'add': lambda a, b: a + b,
    'sub': lambda a, b: a - b,
    'mul': lambda a, b: a * b,
    'div': lambda a, b: np.divide(a, b, out=np.zeros_like(a, dtype=float), where=np.abs(b)>1e-9),
    'pow': lambda a, b: np.nan_to_num(np.sign(a) * (np.abs(a) ** np.clip(b, -3, 3)), nan=0.0, posinf=1e6, neginf=-1e6)
}

def is_valid_tree(tree):
    if isinstance(tree, str): return True
    if isinstance(tree, tuple):
        if tree[0] == 'const': return True
        if tree[0] in BINARY_OPERATORS:
            if len(tree) != 3: return False
            return all(is_valid_tree(c) for c in tree[1:])
    return False

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
    if depth <= 1:
        if random.random() < 0.4: return ('const', random.choice([-2.0, -1.0, 0.5, 1.0, 2.0]))
        return random.choice(features)
    if random.random() < 0.1:
        return ('pow', random.choice(features), ('const', 2.0))
    op = random.choice(list(BINARY_OPERATORS.keys()))
    return (op, random_tree(depth-1, features), random_tree(depth-1, features))

def get_all_nodes(tree, nodes=None):
    if nodes is None: nodes = []
    nodes.append(tree)
    if isinstance(tree, tuple) and tree[0] != 'const':
        for child in tree[1:]:
            get_all_nodes(child, nodes)
    return nodes

def replace_node(tree, target_node, replacement_node):
    if tree == target_node: return replacement_node
    if isinstance(tree, tuple) and tree[0] != 'const':
        return (tree[0], *[replace_node(c, target_node, replacement_node) for c in tree[1:]])
    return tree

def crossover(t1, t2):
    if random.random() < 0.2: return random.choice([t1, t2])
    nodes1 = get_all_nodes(t1)
    nodes2 = get_all_nodes(t2)
    target1 = random.choice(nodes1)
    target2 = random.choice(nodes2)
    child = replace_node(t1, target1, target2)
    return child if is_valid_tree(child) else t1

def mutate(tree, features, prob=0.2):
    if isinstance(tree, tuple) and tree[0] == 'const':
        if random.random() < prob: return ('const', tree[1] + random.uniform(-0.5, 0.5))
        return tree
    if isinstance(tree, tuple) and tree[0] == 'pow': return tree
    if random.random() < prob: return random_tree(3, features)
    if isinstance(tree, str): return tree
    return (tree[0], *[mutate(c, features, prob) for c in tree[1:]])

def tree_to_sympy(tree):
    if isinstance(tree, str): return sp.Symbol(tree)
    if isinstance(tree, tuple):
        if tree[0] == 'const': return sp.Float(tree[1])
        op = tree[0]
        left = tree_to_sympy(tree[1])
        right = tree_to_sympy(tree[2])
        if op == 'add': return left + right
        if op == 'sub': return left - right
        if op == 'mul': return left * right
        if op == 'div': return left / right
        if op == 'pow': return left ** right
    return sp.Float(0.0)

def gp_core_single(X_raw, y_target, features, generations=30, pop_size=300, max_nodes=20):
    population = [t for t in (random_tree(4, features) for _ in range(pop_size)) if is_valid_tree(t)]
    best_mse = float('inf')
    best_tree = None
    best_scaling = (1.0, 0.0)
    
    for gen in range(generations):
        fitness = []
        for tree in population:
            try:
                if tree_nodes(tree) > max_nodes or not has_vars(tree): continue
                pred = evaluate_tree_safe(tree, X_raw, features)
                if not np.all(np.isfinite(pred)): pred = np.nan_to_num(pred, nan=0.0)
                if np.all(pred == pred[0]): continue
                
                A = np.column_stack([pred, np.ones_like(pred)])
                coef, _, _, _ = np.linalg.lstsq(A, y_target, rcond=None)
                a, b = coef[0], coef[1]
                mse = np.mean((y_target - (a * pred + b))**2)
                
                if not np.isfinite(mse): continue
                fitness.append((mse + 0.001 * tree_nodes(tree), mse, tree, (a, b)))
            except: pass
            
        if not fitness: break
        fitness.sort(key=lambda x: x[0])
        
        if fitness[0][1] < best_mse:
            best_mse = fitness[0][1]
            best_tree = fitness[0][2]
            best_scaling = fitness[0][3]
            
        new_pop = [best_tree]
        while len(new_pop) < pop_size:
            t1 = random.sample(fitness, min(3, len(fitness))); t1.sort(key=lambda x: x[0])
            t2 = random.sample(fitness, min(3, len(fitness))); t2.sort(key=lambda x: x[0])
            child = mutate(crossover(t1[0][2], t2[0][2]), features, prob=max(0.1, 0.3*(1-gen/generations)))
            if tree_nodes(child) > max_nodes or not is_valid_tree(child): continue
            new_pop.append(child)
        population = new_pop
        
    return best_tree, best_mse, best_scaling

# ==========================================
# بخش اجرای دمو (فقط زمانی اجرا می‌شود که فایل مستقیماً صدا زده شود)
# ==========================================
if __name__ == "__main__":
    np.random.seed(42)
    random.seed(42)
    
    print("🌌 شکار در بعد ۹ (نسخه v41 - فتح ۱۰۰٪ با ۸ مرحله)")
    print("="*60)
    
    n_samples = 500
    features = [f"x{i}" for i in range(9)]
    X = np.random.uniform(0.1, 2.0, (n_samples, 9))
    y = 2.5 * X[:, 0]**2 + 1.2 * X[:, 1] * X[:, 2] - 0.8 * X[:, 3] / (X[:, 4] + 1) + np.random.normal(0, 0.05, n_samples)
    
    start = time.time()
    found_trees = []
    current_pred = np.zeros_like(y)
    
    print("⏳ شروع فرآیند تقویت باقیمانده (تا ۸ مرحله)...")
    for stage in range(8):
        print(f"🔍 مرحله {stage+1}: در حال جستجوی جمله بعدی...")
        residual = y - current_pred
        
        best_tree, best_mse, best_scaling = gp_core_single(X, residual, features, generations=10, pop_size=100)
        
        if best_tree is not None:
            pred = evaluate_tree_safe(best_tree, X, features)
            a, b = best_scaling
            current_pred += a * pred + b
            found_trees.append((best_tree, a, b))
            
            r2_val = 1 - np.sum((y - current_pred)**2) / np.sum((y - y.mean())**2)
            print(f"📜 کشف شد: {str(best_tree)[:40]}... | خطای باقیمانده: {best_mse:.4f}")
        else:
            break
            
    print("="*60)
    emoji = "🏆" if r2_val > 0.9 else "📊"
    print(f"{emoji} دقت نهایی (R²): {r2_val:.4f}")
    print(f"⏱️ زمان کل: {time.time() - start:.1f} ثانیه")
    
    print("\n✨ فرمول نهایی (ترکیب تمام مراحل):")
    try:
        final_sympy_expr = sp.Float(0.0)
        for tree, a, b in found_trees:
            expr = tree_to_sympy(tree)
            final_sympy_expr += (a * expr + b)
        simplified = sp.factor(sp.simplify(final_sympy_expr))
        print(simplified)
    except Exception as e:
        print(f"خطا در ساده‌سازی: {e}")
