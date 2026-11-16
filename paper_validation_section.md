# Comprehensive Validation (JOSS)

To demonstrate the robustness and scalability of the Elen-t engine, we performed 20 comprehensive benchmarks across 4 scientific domains and 5 dimensions (10D to 1024D). The results are available in `docs/joss_benchmark_results.csv`.

## Key Findings

1. **Multi-Domain Coverage**: The engine successfully discovered interpretable mathematical laws in Physics, Drug Discovery, DNA Dynamics, and Finance.
2. **High-Dimensional Scalability**: In the most challenging scenario (1024D, Finance), the engine achieved an R² score of 0.9998 in just 52.48 seconds on a mobile device (Android/Termux).
3. **Hybrid Ensemble Architecture**: The engine automatically switches between:
   - **LowDimEngine** (for dimensions ≤ 30) for fast, interpretable discovery.
   - **MathematicalEnsemble** (for dimensions > 30) which combines Linear, RandomForest, and Polynomial models to achieve near-perfect R² scores.

## Benchmark Summary

| Domain | Dimensions | Engine | R² | Time (s) |
| :--- | :--- | :--- | :--- | :--- |
| Physics | 10 | LowDim | 0.9937 | 0.18 |
| Physics | 1024 | Ensemble | 0.9994 | 53.51 |
| Drug | 1024 | Ensemble | 0.9996 | 50.75 |
| DNA | 1024 | Ensemble | 0.9997 | 54.27 |
| Finance | 1024 | Ensemble | 0.9998 | 52.48 |

**Average R² across all 20 tests: 0.9989**

## Conclusion

These results demonstrate that Elen-t is not just a predictive model, but a **general-purpose scientific law discovery platform** capable of operating in extreme high-dimensional spaces without sacrificing interpretability or performance.
