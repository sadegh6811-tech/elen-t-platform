import numpy as np
import random
import time
import sys
import traceback

# اضافه کردن مسیر برای ایمپورت
sys.path.insert(0, '/data/data/com.termux/files/home/elen')
from lab_1024d_log_space import gp_core_single, evaluate_tree_safe

def run_unleashed():
    print("="*60)
    print("🌌 ELEN-T: 1024D LOG-SPACE (UNLEASHED max_nodes=35)")
    print("="*60)
    
    np.random.seed(42)
    random.seed(42)
    n_samples = 500
    
    # 1. تولید داده‌های ۱۰۲۴ بعدی
    X_raw = np.random.uniform(0.5, 2.0, (n_samples, 1024))
    
    # 2. ترفند لگاریتمی (کاهش ابعاد به ۴ گروه)
    A_group = np.sum(X_raw[:, 0:256], axis=1) + 1.0
    B_group = np.sum(X_raw[:, 256:512], axis=1) + 1.0
    C_group = np.sum(X_raw[:, 512:768], axis=1) + 1.0
    D_group = np.sum(X_raw[:, 768:1024], axis=1) + 1.0
    
    log_A = np.log(A_group)
    log_B = np.log(B_group)
    log_C = np.log(C_group)
    log_D = np.log(D_group)
    
    X_features = np.column_stack([log_A, log_B, log_C, log_D])
    features = ['log_A', 'log_B', 'log_C', 'log_D']
    
    # 3. هدف: مجموع لگاریتم‌ها (با نویز کم)
    y_target = log_A + log_B + log_C + log_D + np.random.normal(0, 0.01, n_samples)
    
    # 4. تقسیم داده‌ها
    split_idx = int(n_samples * 0.8)
    X_train, X_test = X_features[:split_idx], X_features[split_idx:]
    y_train, y_test = y_target[:split_idx], y_target[split_idx:]
    
    # 5. نرمال‌سازی (بسیار مهم برای GP)
    X_m, X_s = X_train.mean(0), X_train.std(0)
    X_s[X_s < 1e-9] = 1.0
    X_train_n = (X_train - X_m) / X_s
    X_test_n = (X_test - X_m) / X_s
    
    y_m, y_s = y_train.mean(), y_train.std()
    y_train_n = (y_train - y_m) / y_s
    y_test_n = (y_test - y_m) / y_s
    
    print("⏳ Running GP with max_nodes=35...")
    start_t = time.time()
    
    # 6. اجرای موتور (با مدیریت خطا)
    try:
        result = gp_core_single(X_train_n, y_train_n, features, generations=30, pop_size=300, max_nodes=35)
    except Exception as e:
        print(f"❌ GP Engine crashed: {e}")
        traceback.print_exc()
        return

    # 7. مدیریت هوشمند خروجی‌های موتور
    if result is None:
        print("❌ Engine returned None.")
        return
        
    if isinstance(result, tuple):
        if len(result) == 3:
            best_tree, mse, scaling = result
        elif len(result) == 2:
            best_tree, mse = result
            scaling = (1.0, 0.0)
        elif len(result) == 1:
            best_tree = result[0]
            scaling = (1.0, 0.0)
        else:
            print(f"❌ Unexpected return length: {len(result)}")
            return
    else:
        best_tree = result
        scaling = (1.0, 0.0)

    if best_tree is None:
        print("❌ GP failed to find a valid tree (max_nodes might be too small or search space too large).")
        return

    # 8. ارزیابی
    try:
        pred_test = evaluate_tree_safe(best_tree, X_test_n, features)
        pred_test = np.nan_to_num(pred_test, nan=0.0, posinf=1e6, neginf=-1e6)
        
        # مدیریت فرمت scaling
        if isinstance(scaling, (tuple, list)) and len(scaling) == 2:
            a, b = scaling
        elif isinstance(scaling, (int, float)):
            a, b = scaling, 0.0
        else:
            a, b = 1.0, 0.0
            
        y_pred = a * pred_test + b
        
        ss_res = np.sum((y_test_n - y_pred)**2)
        ss_tot = np.sum((y_test_n - y_test_n.mean())**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        
        print(f"✅ Done in {time.time() - start_t:.1f}s")
        print(f"🏆 R² Score: {r2:.4f}")
        print(f"📜 Formula: {str(best_tree)[:100]}...")
        
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_unleashed()
