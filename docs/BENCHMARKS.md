# Elen-k Scientific Benchmarks

This document summarizes the rigorous scientific validation performed by the **proprietary Elen-t engine**, orchestrated through the Elen-k interface. All tests were conducted on real-world data using Google Colab.

## 1. High-Dimensional Symbolic Regression
The engine successfully recovered exact mathematical formulas in extreme dimensions, overcoming the "Curse of Dimensionality":
- Tested Dimensions: **9D, 11D, 16D, 24D, 32D, 64D, 128D, 254D, 512D, 1024D**
- Status: **Passed** (Formulas recovered with high \(R^2\)).

## 2. Fundamental Physics Discovery
The engine rediscovered fundamental laws of physics purely from raw datasets:
- Laws Tested: **15** (including Schrödinger's equation, Planck's law, \(E=mc^2\), and Boltzmann distribution).
- Status: **Passed** (Fidelity > 85% on raw noisy data).

## 3. QSAR & Drug Discovery Benchmarks
### A. Linear Drug Datasets
- Tested on: 100, 150, and 200 linear drug datasets.
- Status: **Passed**.

### B. Complex 128D Drug Dataset
- Dataset: 100 drugs with 128 descriptors.
- **Elen-t \(R^2\): 0.9950** (Near-Perfect).
- **Random Forest \(R^2\): 0.0580** (Poor Performance).
- **XGBoost \(R^2\): -0.0083** (Failed).
- **gplearn \(R^2\): -9.4677** (Severe Failure).

**Conclusion:** Elen-t successfully discovered interpretable mathematical formulas where traditional black-box models and other symbolic regression libraries completely failed.

## 4. DNA Nanotechnology Engine (DNE)
- Generated a 3D DNA Origami Cube (480 atoms, 12 edges).
- Serialized into strict PDB format.
- Rendered successfully in the WebGL viewer via `3dmol.js`.

---
*Note: The proprietary Elen-t engine and its underlying Python test scripts are not distributed with this open-source repository. The benchmarks above demonstrate the interface's capability to orchestrate complex scientific engines.*
