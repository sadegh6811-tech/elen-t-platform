import numpy as np
import random

# ═══════════════════════════════════════════════════════════
# 1. OPERATORS (Only Safe Ones)
# ═══════════════════════════════════════════════════════════
# ما فقط از عملگرهای امن استفاده می‌کنیم تا در ابعاد بالا گم نشویم
BINARY_OPERATORS = {
    'add': lambda a, b: a + b,
    'sub': lambda a, b: a - b,
    'mul': lambda a, b: a * b,
    'div': lambda a, b: np.divide(a, b + 1e-9) # جلوگیری از تقسیم بر صفر
}

# ═══════════════════════════════════════════════════════════
# 2. TREE UTILITIES
# ═══════════════════════════════════════════════════════════
def evaluate_tree_safe(tree, X, features):
    if isinstance(tree, str):
        if tree not in features:
            raise ValueError(f'Unknown feature: {tree}')
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
    if depth <= 0:
        # تقویت ثابت‌ها (مخصوصاً 0.5 برای معادلات فیزیک)
        if random.random() < 0.4: return ('const', random.choice([-1.0, 1.0, 2.0, 0.5]))
        return random.choice(features)
    op = random.choice(list(BINARY_OPERATORS.keys()))
    return (op, random_tree(depth-1, features), random_tree(depth-1, features))

# ═══════════════════════════════════════════════════════════
# 3. GENETIC OPERATORS
# ═══════════════════════════════════════════════════════════
def get_all_nodes(tree):
    nodes = [tree]
    if isinstance(tree, tuple):
        if tree[0] == 'const': return nodes
        for child in tree[1:]:
            nodes.extend(get_all_nodes(child))
    return nodes

def replace_node(tree, target_node, replacement_node):
    if tree == target_node:
        return replacement_node
    if isinstance(tree, tuple):
        if tree[0] == 'const': return tree
        new_children = [replace_node(child, target_node, replacement_node) for child in tree[1:]]
        return (tree[0], *new_children)
    return tree

def crossover(t1, t2):
    if isinstance(t1, (int, float)): t1 = ('const', float(t1))
    if isinstance(t2, (int, float)): t2 = ('const', float(t2))
    if random.random() < 0.2: return random.choice([t1, t2])
    nodes1 = get_all_nodes(t1)
    nodes2 = get_all_nodes(t2)
    return replace_node(t1, random.choice(nodes1), random.choice(nodes2))

def mutate(tree, features, prob=0.2):
    if isinstance(tree, (int, float)): tree = ('const', float(tree))
    if isinstance(tree, tuple) and tree[0] == 'const':
        if random.random() < prob:
            return ('const', tree[1] + random.uniform(-0.2, 0.2)) 
        return tree
    if random.random() < prob: return random_tree(3, features)
    if isinstance(tree, str): return tree
    return (tree[0], mutate(tree[1], features, prob), mutate(tree[2], features, prob))

# ═══════════════════════════════════════════════════════════
# 4. MAIN ENGINE (GP Core)
# ═══════════════════════════════════════════════════════════
def gp_core_v31(X_raw, y_raw, features, generations=80, pop_size=300, max_nodes=15):
    population = [random_tree(3, features) for _ in range(pop_size)]
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
                if not np.all(np.isfinite(pred)): pred = np.nan_to_num(pred, nan=0.0)

                mse = np.mean((y_raw - pred)**2)
                if not np.isfinite(mse): continue

                complexity_penalty = 0.01 * nodes
                score = mse + complexity_penalty
                fitness.append((score, mse, tree))
            except Exception:
                pass

        if not fitness: break
        fitness.sort(key=lambda x: x[0])

        if fitness[0][1] < best_mse:
            best_mse = fitness[0][1]
            best_tree = fitness[0][2]

        new_pop = [best_tree]
        while len(new_pop) < pop_size:
            t1 = random.sample(fitness, min(3, len(fitness))); t1.sort(key=lambda x: x[0])
            t2 = random.sample(fitness, min(3, len(fitness))); t2.sort(key=lambda x: x[0])
            # کاهش تدریجی نرخ جهش
            child = mutate(crossover(t1[0][2], t2[0][2]), features, prob=max(0.1, 0.3*(1-gen/generations)))
            if tree_nodes(child) > max_nodes: child = random_tree(3, features)
            new_pop.append(child)
        population = new_pop
        
    return best_tree, best_mse
