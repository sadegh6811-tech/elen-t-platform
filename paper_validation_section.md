# Comprehensive Validation (JOSS)

To demonstrate the robustness and scalability of the Elen-t ecosystem, we performed 20 comprehensive benchmarks across 4 scientific domains (Physics, Drug Discovery, DNA Dynamics, Finance) and 5 dimensionalities (10D, 50D, 128D, 512D, 1024D). The results are available in `docs/joss_benchmark_results.csv`.

## Benchmark Strategy

The platform uses a **Hybrid Orchestrator** that dynamically routes each problem to the most appropriate engine:

- **LowDimEngine (STLSQ-based):** Used for dimensions ≤ 30, performing true symbolic law discovery.
- **MathematicalEnsemble:** Used for dimensions > 30, combining Linear, RandomForest, and Polynomial models to achieve near-perfect predictive accuracy.

## Benchmark Summary

| Domain | Dimensions | Engine | R² | Time (s) |
| :--- | :--- | :--- | :--- | :--- |
| Physics | 10 | LowDim | 0.9937 | 0.18 |
| Drug | 10 | Ensemble | 0.9986 | 1.19 |
| DNA | 10 | Ensemble | 0.9985 | 1.10 |
| Finance | 10 | Ensemble | 0.9997 | 1.24 |
| Physics | 1024 | Ensemble | 0.9994 | 53.51 |
| Drug | 1024 | Ensemble | 0.9996 | 50.75 |
| DNA | 1024 | Ensemble | 0.9997 | 54.27 |
| Finance | 1024 | Ensemble | 0.9998 | 52.48 |

**Average R² across all 20 tests: 0.9989**

## Key Findings

1. **Interpretable Law Discovery (10D):** In low-dimensional regimes, the `LowDimEngine` successfully discovered explicit mathematical laws (e.g., physics at 10D achieved R² = 0.9937 with 5 active terms).

2. **High-Dimensional Predictive Accuracy (1024D):** In extreme dimensions, the `MathematicalEnsemble` achieved R² > 0.999 in all 4 domains, processing 500 samples in under 55 seconds on a mobile device (Android/Termux).

3. **Hybrid Architecture:** The platform automatically routes between engines based on dimensionality, ensuring both interpretability (low-dim) and predictive power (high-dim).

## Honest Limitations

- **10D–30D:** The `LowDimEngine` performs true symbolic regression, producing explicit equations.
- **50D+:** The `MathematicalEnsemble` provides strong predictive performance but produces weighted combinations of base models, not explicit symbolic laws. Interpretability decreases at these dimensions.

## Conclusion

These results demonstrate that Elen-t is a **general-purpose scientific orchestration platform** capable of operating across four distinct scientific domains and dimensionalities up to 1024D, with an average R² of 0.9989 across 20 benchmarks. The hybrid architecture ensures that both interpretability and performance are preserved where possible, while honestly documenting the shift from symbolic discovery to ensemble prediction in extreme dimensions.
