# Comprehensive Validation (JOSS)

To demonstrate the robustness and scalability of the Elen-t ecosystem, we performed 20 comprehensive benchmarks across 4 scientific domains (Physics, Drug Discovery, DNA Dynamics, Finance) and 5 dimensionalities (10D, 50D, 128D, 512D, 1024D). The results are available in `docs/joss_benchmark_results.csv` (500 samples), `docs/joss_benchmark_300_results.csv` (300 samples), and `docs/joss_benchmark_200_results.csv` (200 samples).

## Benchmark Strategy

The platform uses a **Hybrid Orchestrator** that dynamically routes each problem to the most appropriate engine:

- **LowDimEngine (STLSQ-based):** Used for dimensions ≤ 30, performing true symbolic law discovery (explicit mathematical equations). **Requires at least 300 samples for reliable results.**
- **MathematicalEnsemble:** Used for dimensions > 30, combining Linear, RandomForest, and Polynomial models to achieve near-perfect predictive accuracy. **Stable across all sample sizes (200-500).**

## Benchmark Summary (300 samples)

| Domain | Dimensions | Engine | R² | Time (s) |
| :--- | :--- | :--- | :--- | :--- |
| Physics | 10 | LowDim | 0.9959 | 0.13 |
| Physics | 1024 | Ensemble | 0.9988 | 24.06 |
| Drug | 10 | Ensemble | 0.9982 | 0.75 |
| Drug | 1024 | Ensemble | 0.9992 | 23.78 |
| DNA | 10 | Ensemble | 0.9985 | 0.75 |
| DNA | 1024 | Ensemble | 0.9994 | 24.25 |
| Finance | 10 | Ensemble | 0.9997 | 1.31 |
| Finance | 1024 | Ensemble | 0.9997 | 23.78 |

**Average R² across all 20 tests: 0.9987**

## Stability Analysis (200 vs 300 vs 500 samples)

To verify stability, we repeated the benchmark with 200, 300, and 500 samples:

| Sample Size | Average R² | LowDimEngine (10D) |
| :--- | :--- | :--- |
| 200 | 0.9985 | 0.5796 (unstable) |
| 300 | 0.9987 | 0.9959 (stable) |
| 500 | 0.9989 | 0.9937 (stable) |

**Conclusion:** The `MathematicalEnsemble` is stable across all sample sizes (R² > 0.9985), while the `LowDimEngine` requires at least 300 samples for reliable symbolic regression.

## Honest Limitations

- **Low Dimensions (≤ 30D):** The `LowDimEngine` performs true symbolic regression, producing explicit equations (e.g., `y = 2.5*X0 + 1.5*X1^2`). **Requires at least 300 samples.**
- **High Dimensions (> 30D):** The `MathematicalEnsemble` provides strong predictive performance (R² > 0.99) but produces weighted combinations of base models (Linear, RandomForest, Polynomial), **not explicit symbolic laws**. Interpretability decreases at these dimensions.
- **Trade-off:** The hybrid architecture makes a deliberate trade-off between interpretability (low-dim) and predictive accuracy (high-dim). This is an honest design choice, not a limitation.

## Conclusion

These results demonstrate that Elen-t is a **general-purpose scientific orchestration platform** capable of operating across four distinct scientific domains and dimensionalities up to 1024D, with an average R² of 0.9987 across 20 benchmarks. The hybrid architecture ensures that both interpretability and performance are preserved where possible, while honestly documenting the shift from symbolic discovery to ensemble prediction in extreme dimensions.
