# Appendix A: Computational Methods

## A.1 Software Environment

- **Language:** Python 3.14.6 (CPython)
- **Core libraries:** NumPy >= 1.20, SciPy >= 1.7
- **Platform:** Termux (Android), aarch64 architecture
- **Code size:** ~400 lines total

## A.2 Sparse Symbolic Regression (OMP + BIC)

### A.2.1 Algorithm

The algorithm proceeds in five steps:

1. **Feature construction:** All products of base functions [X_i, cos(X_i), sin(X_i)] up to polynomial degree d are generated. For d = 4 and 5 input variables, this yields 15,504 features.
2. **Column normalization:** Each feature column is normalized to unit L2 norm.
3. **Greedy selection (OMP):** At each iteration, the feature most correlated with the current residual is added to the active set.
4. **Coefficient re-estimation:** After each addition, least-squares re-estimation is performed.
5. **Stopping criterion (BIC):** If the new term increases BIC or provides less than 5% relative MSE improvement, the term is rejected.

### A.2.2 Verification

On synthetic data generated from Phi = T * A_c * A_e * f * cos(dphi) with 3000 points:

- Number of selected terms: 1
- Coefficient: 1.00000000
- R^2: 1.0000000000
- RMSE: 1.14e-10

## A.3 Lindblad Master Equation Solver

### A.3.1 System Specification

- Mental state: two-level system (|g>, |e>)
- Phonon mode: Fock space truncated at n_max = 10
- Hilbert space dimension: 20
- Hamiltonian: H = 0.5 sz + a^dag a + g(a^dag s- + a s+)
- Dissipators: three channels (mental, phonon, dephasing)
- Integration: scipy.integrate.solve_ivp with RK45, rtol=1e-6, atol=1e-8

### A.3.2 Data Tables

**Table A.3.1: Single-mode time evolution** (g = 0.10)

| Time | <n_ph> | Coherence |
|---|---|---|
| 0.0 | 0.100 | 0.500 |
| 5.0 | 0.175 | 0.275 |
| 10.0 | 0.274 | 0.077 |
| 12.6 | 0.288 | (peak) |
| 25.0 | 0.132 | 0.136 |
| 50.0 | 0.066 | 0.012 |

**Table A.3.2: Sweep in coupling g**

| g | n_max | tau_coh | Net transfer |
|---|---|---|---|
| 0.01 | 0.100 | 11.70 | 0.000 |
| 0.05 | 0.179 | 9.70 | 0.079 |
| 0.10 | 0.288 | 7.20 | 0.188 |
| 0.20 | 0.387 | 4.50 | 0.287 |
| 0.30 | 0.430 | 3.30 | 0.330 |

**Table A.3.3: Sweep in dephasing rate gamma_phi**

| gamma_phi | n_max | tau_coh |
|---|---|---|
| 0.00 | 0.334 | 10.10 |
| 0.01 | 0.317 | 9.00 |
| 0.03 | 0.288 | 7.20 |
| 0.10 | 0.225 | 3.90 |
| 0.30 | 0.158 | 1.60 |

**Table A.3.4: Sweep in thermal phonon number n_th**

| n_th | n_max | Net transfer |
|---|---|---|
| 0.00 | 0.243 | 0.243 |
| 0.05 | 0.264 | 0.214 |
| 0.10 | 0.288 | 0.188 |
| 0.30 | 0.404 | 0.104 |
| 1.00 | 0.990 | -0.010 |

## A.4 Frohlich Condensation Simulation

### A.4.1 System Specification

- Number of phonon modes: 3
- Fock space truncation: n_max = 3
- Hilbert space dimension: 64
- Mode frequencies: omega_k = 1.0 + 0.4 k
- Inter-mode coupling: lambda = 0.03
- Phonon decay: gamma_ph = 0.02
- Effective temperature: T_eff = 0.3
- Integration time: T_dur = 10.0
- Integrator: RK45, rtol=1e-2, atol=1e-4

### A.4.2 Data Table

**Table A.4.1: Frohlich condensation sweep**

| Phi | <n_0> | <n_1> | <n_2> | r_10 |
|---|---|---|---|---|
| 0.00 | 0.031 | 0.008 | 0.001 | 0.266 |
| 0.01 | 0.127 | 0.009 | 0.002 | 0.074 |
| 0.02 | 0.232 | 0.011 | 0.002 | 0.046 |
| 0.05 | 0.585 | 0.015 | 0.003 | 0.026 |
| 0.10 | 1.203 | 0.023 | 0.005 | 0.019 |
| 0.20 | 2.143 | 0.036 | 0.011 | 0.017 |
| 0.40 | 2.821 | 0.045 | 0.021 | 0.016 |
| 0.80 | 2.967 | 0.039 | 0.026 | 0.013 |
| 1.50 | 2.978 | 0.027 | 0.020 | 0.009 |

**Trace verification:** Density matrix trace remains at 1.00000000.

### A.4.3 Critical Threshold

- Between Phi = 0.00 and Phi = 0.02, r_10 drops by factor 5.8
- Estimated critical value: Phi_c ~ 0.02

## A.5 Figures

Five SVG figures:

1. fig1_lindblad_time.svg - Time evolution
2. fig2_scaling_laws.svg - Three scaling laws
3. fig3_phi_powerlaw.svg - Power-law Phi to E
4. fig4_frohlich.svg - Frohlich condensation
5. fig5_phase_diagram.svg - Phase diagram

## A.6 Reproducibility

Run: python appendix_code.py

Random seed fixed at 42 in all stochastic components.

**End of Appendix A**
