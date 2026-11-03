"""v13_core: Pure GP functions from discover_all_physics_v13.
No executable code at module level — safe for multiprocessing.
"""

import numpy as np
import random

# ═══════════════════════════════════════════════════════════
# Operators (from v13)
# ═══════════════════════════════════════════════════════════
def safe_log(x): return np.log(np.abs(x) + 1e-9)
def safe_sqrt(x): return np.sqrt(np.abs(x) + 1e-9)
def safe_exp(x): return np.exp(np.clip(x, -5, 5))
def safe_pow(a, b):
    base = np.clip(np.abs(a), 1e-9, 10.0)
    exp = np.clip(b, -3, 3)
    return np.sign(a) * (base ** exp)
def safe_div(a, b): return np.divide(a, b + 1e-9)

UNARY_OPERATORS = {'log': safe_log, 'sqrt': safe_sqrt, 'exp': safe_exp, 'abs': np.abs}
BINARY_OPERATORS = {
    'add': lambda a, b: a + b,
    'sub': lambda a, b: a - b,
    'mul': lambda a, b: a * b,
    'div': safe_div,
    'pow': safe_pow,
}

# ═══════════════════════════════════════════════════════════
# Tree functions
# ═══════════════════════════════════════════════════════════
def evaluate_tree_safe(tree, X, features):
    if tree is None:
        return np.zeros(X.shape[0])
    if isinstance(tree, str):
        if tree not in features: return np.zeros(X.shape[0])
        return X[:, features.index(tree)]
    if isinstance(tree, tuple):
        if len(tree) == 0 or tree[0] is None:
            return np.zeros(X.shape[0])
        if tree[0] == 'const':
            try:
                return np.full(X.shape[0], float(tree[1]))
            except (ValueError, TypeError):
                return np.zeros(X.shape[0])
        op = tree[0]
        if op in UNARY_OPERATORS:
            try:
                return UNARY_OPERATORS[op](evaluate_tree_safe(tree[1], X, features))
            except:
                return np.zeros(X.shape[0])
        elif op in BINARY_OPERATORS:
            try:
                left = evaluate_tree_safe(tree[1], X, features)
                right = evaluate_tree_safe(tree[2], X, features)
                return BINARY_OPERATORS[op](left, right)
            except:
                return np.zeros(X.shape[0])
    return np.zeros(X.shape[0])

def tree_nodes(tree):
    if tree is None: return 0
    if isinstance(tree, (str, int, float)): return 1
    if isinstance(tree, tuple):
        if len(tree) == 0: return 0
        if tree[0] == 'const': return 1
        return 1 + sum(tree_nodes(c) for c in tree[1:])
    return 0

def has_vars(tree):
    if tree is None: return False
    if isinstance(tree, str): return True
    if isinstance(tree, tuple):
        if len(tree) == 0: return False
        if tree[0] == 'const': return False
        return any(has_vars(c) for c in tree[1:])
    return False

def random_tree(depth, features):
    if depth <= 0:
        if random.random() < 0.3:
            return ('const', random.choice([-1.0, -0.5, 0.5, 1.0, 2.0]))
        return random.choice(features)
    r = random.random()
    if r < 0.25:
        op = random.choice(list(UNARY_OPERATORS.keys()))
        return (op, random_tree(depth-1, features))
    op = random.choice(list(BINARY_OPERATORS.keys()))
    return (op, random_tree(depth-1, features), random_tree(depth-1, features))

def mutate(tree, features, prob=0.2):
    if random.random() < prob:
        return random_tree(3, features)
    if isinstance(tree, str): return tree
    if isinstance(tree, tuple):
        if len(tree) == 0: return random_tree(3, features)
        if tree[0] == 'const': return tree
        if tree[0] in UNARY_OPERATORS:
            return (tree[0], mutate(tree[1], features, prob))
        if tree[0] in BINARY_OPERATORS:
            return (tree[0],
                    mutate(tree[1], features, prob),
                    mutate(tree[2], features, prob))
    return tree

def crossover(t1, t2):
    if random.random() < 0.2: return random.choice([t1, t2])
    nodes1 = []
    def collect(t):
        nodes1.append(t)
        if isinstance(t, tuple) and len(t) > 0:
            if t[0] in BINARY_OPERATORS:
                collect(t[1]); collect(t[2])
            elif t[0] in UNARY_OPERATORS:
                collect(t[1])
    collect(t1)
    nodes2 = []
    def collect2(t):
        nodes2.append(t)
        if isinstance(t, tuple) and len(t) > 0:
            if t[0] in BINARY_OPERATORS:
                collect2(t[1]); collect2(t[2])
            elif t[0] in UNARY_OPERATORS:
                collect2(t[1])
    collect2(t2)
    target = random.choice(nodes1)
    replacement = random.choice(nodes2)
    def replace(t):
        if t == target: return replacement
        if isinstance(t, tuple) and len(t) > 0:
            if t[0] in BINARY_OPERATORS:
                return (t[0], replace(t[1]), replace(t[2]))
            elif t[0] in UNARY_OPERATORS:
                return (t[0], replace(t[1]))
        return t
    return replace(t1)

# ═══════════════════════════════════════════════════════════
# Pure GP Core (extracted from v13, no executable code)
# ═══════════════════════════════════════════════════════════
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
            break
        fitness.sort(key=lambda x: x[0])

        if fitness[0][1] < best_mse:
            best_mse = fitness[0][1]
            best_tree = fitness[0][2]

        new_pop = [best_tree] if best_tree is not None else []
        while len(new_pop) < pop_size:
            t1 = random.sample(fitness, min(3, len(fitness))); t1.sort(key=lambda x: x[0])
            t2 = random.sample(fitness, min(3, len(fitness))); t2.sort(key=lambda x: x[0])
            child = mutate(crossover(t1[0][2], t2[0][2]), features,
                           prob=max(0.05, 0.3*(1-gen/generations)))
            if tree_nodes(child) > max_nodes: child = random_tree(3, features)
            new_pop.append(child)
        population = new_pop

    return best_tree, best_mse
