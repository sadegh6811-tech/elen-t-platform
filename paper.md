---
title: 'Elen-t: A Genetic Programming Engine for Symbolic Discovery in High-Dimensional Spaces'
tags:
  - Python
  - symbolic regression
  - genetic programming
  - scientific discovery
  - drug discovery
authors:
  - name: Sadegh Karami Chafteh
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 05 November 2026
bibliography: paper.bib
---

# Summary

Elen-t is an open-source Python library for symbolic regression: it recovers interpretable mathematical expressions from high-dimensional datasets using genetic programming. The ecosystem includes Elen-k, a unified dashboard for managing computational experiments.

# Statement of need

In fields such as physics, chemistry, and drug discovery, researchers require not only accurate predictions but also the underlying mathematical laws. Black-box models (e.g., Random Forest, XGBoost) fail in high-dimensional spaces. Elen-t addresses this by providing a robust engine that actively constructs mathematical expressions.

# State of the field

Current symbolic regression tools (e.g., gplearn, PySR) are powerful but often lack an integrated environment for managing high-dimensional benchmarks. Our benchmarks demonstrate that while standard models (RF, XGBoost) and baseline GP (gplearn) fail catastrophically in 128-dimensional spaces (achieving R^2 scores near zero or negative), Elen-t successfully recovers the underlying formulas, achieving R^2 scores up to 0.995.

# Software design

The core module implements a strongly-typed genetic-programming loop. To handle high-dimensional spaces, we introduce a *log-grouped aggregation* frontend. For a 1024-dimensional raw input, features are aggregated into 4 log-transformed groups before symbolic regression. NumPy and Pandas handle data I/O; Elen-k is a React frontend.

# Research impact statement

Elen-t has demonstrated significant potential in drug discovery, recovering nonlinear molecular relationships with 99.5% accuracy while producing human-readable formulas.

# AI usage disclosure

AI-assisted tools were used for code scaffolding and documentation editing. All algorithms, scientific logic, and validation were designed and verified by the author.

# Acknowledgements

The author thanks the open-source community behind NumPy, Pandas, and the React ecosystem.

# References
