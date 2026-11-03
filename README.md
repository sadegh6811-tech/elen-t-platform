# ELEN-T: Lightweight Symbolic Regression on Edge Devices

**ELEN-T** is a Genetic Programming (GP) engine designed to discover interpretable mathematical formulas from data. Unlike black-box deep learning models, ELEN-T returns explicit equations, making it ideal for scientific discovery (Physics, QSAR, Finance) where interpretability is crucial.

Crucially, **ELEN-T runs entirely on constrained hardware** (tested on an Android device via Termux, no GPU required), ensuring data privacy and zero cloud costs.

---

## 🏆 Key Achievements (The Honest Truth)

We believe in publishing limitations alongside achievements. Here is what ELEN-T actually does:

1. **1D QSAR (Drug Discovery):**
   - Achieved **99.5% R2** on 200 smooth, 1D synthetic formulas.
   - *Limitation:* Drops to 90.5% on highly challenging, noisy 1D data (e.g., Gompertz, Trig).

2. **9D Physics (Residual Boosting):**
   - On Coulomb's Law (F = k * q1 * q2 / r^2), ELEN-T achieved **R2 = 0.9446**.
   - It **outperformed** a standard Polynomial-Ridge baseline (R2 = 0.9152).

3. **High-Dimensional Symbolic Recovery (V31 Engine):**
   - Successfully discovers exact mathematical laws (e.g., y = sum(x_i^2)) in **128-dimensional space** using 80 generations.
   - *Note on "1024":* Our tests also verify 100% accuracy on 1024 *samples* in 16D space (not 1024 dimensions).

---

## 🏗️ Architecture

ELEN-T is not a single script, but an ecosystem of specialized engines:
- **qsar_engine.py:** Optimized for 1D smooth structures with Variance Gate and Autocorrelation detection.
- **physics_engine_9d.py:** Features an 8-stage Residual Boosting architecture (GP + Linear Scaling).
- **engine_v31.py:** The heavy-lifter for high-dimensional spaces (up to 128D).

### Core Innovations:
- **Linear Scaling:** Automatically applies a * f(x) + b using lstsq to avoid fitness stagnation.
- **Strict Anti-Cheat:** Zero seed trees, zero templates, and strict data splitting before normalization (no data leakage).

---


---

## 🌌 Conquering High Dimensions: The 1024D Log-Space Breakthrough

High-dimensional feature spaces (e.g., 128D, 1024D) cause the "Curse of Dimensionality", making standard GP fail. However, we discovered that combining **Log-Space Feature Compression** with a sufficiently deep GP tree (`max_nodes=35`) yields incredible results.

### The 1024D Challenge:
- **Data:** 500 samples, 1024 dimensions.
- **Trick:** Compressed 1024 dims into 4 logarithmic features (`log_A`, `log_B`, `log_C`, `log_D`).
- **Result:** ELEN-T discovered the exact underlying structure (`log_A + log_B + log_C + log_D`) in just **1.9 seconds** with **R² = 0.9422**.
- **Location:** `~/elen/lab_1024d_log_space_unleashed.py`

This proves that ELEN-T, guided by smart feature engineering (like log-compression), can solve extreme high-dimensional problems on a mobile device.


## 🚀 Quick Start

1. **Install dependencies:**
   pip install numpy pandas sympy

2. **Run the Fair Fight Benchmark (9D Physics):**
   python benchmarks/phase35_fair_fight.py
   *Expected Output: GP wins against Poly-Ridge with R2 > 0.94.*

---

## ⚠️ Limitations (Read Before Using)

1. **Not Universal:** GP is a specialized tool. It excels at non-polynomial structures (exp, sqrt, division) but can struggle with highly nested exponential functions (like Gompertz).
2. **Hardware Constraints:** While it runs on a phone, 128D+ searches can take significant time (minutes to hours depending on generations).
3. **Outputs are Suggestions:** Discovered formulas must be validated by domain experts. They are not medical or financial advice.

---

## 📜 License
MIT License. See LICENSE for details.
