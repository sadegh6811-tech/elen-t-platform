---
title: 'Elen-k Health OS: A Bilingual Web Platform for Scientific Law Discovery'
tags:
  - Scientific Software
  - Next.js
  - FastAPI
  - Progressive Web App
  - Bilingual Interface
  - Law Discovery
authors:
  - name: Sadegh Karami Chofteh
    affiliation: Independent Researcher
date: 16 November 2026
---

# Summary

Discovering mathematical laws from raw experimental data typically requires researchers to juggle multiple disconnected tools: a Python environment for symbolic regression (e.g., PySR, SINDy), a separate molecular viewer (e.g., PyMOL, 3Dmol.js), and a third setup for physics simulation. This fragmentation is especially painful for researchers in resource-constrained environments (mobile-only setups, low-bandwidth regions) where installing a full desktop scientific stack is impractical.

`Elen-k Health OS` is an open-source, bilingual (Persian/English) web platform that unifies the entire scientific law discovery loop into a single browser-based workflow. It accepts raw experimental data (CSV/JSON), dynamically routes the problem to the most suitable external scientific engine via a documented REST API, and visualizes the discovered equation and 3D molecular structures in real time. The platform is installable as a Progressive Web App (PWA) on Android and iOS, and runs on free-tier infrastructure (Vercel + Neon PostgreSQL).

# Statement of Need

To our knowledge, no existing open-source platform offers a unified, bilingual, PWA-installable workflow for scientific law discovery. Existing tools are either command-line only (PySR, SINDy) or locked behind proprietary desktop interfaces (MATLAB, Mathematica). Elen-k Health OS fills this gap by providing a mobile-first, open-source interface that:
1. Accepts raw data in standard formats (CSV, JSON).
2. Routes the problem to specialized engines (physics, drug discovery, DNA nanotechnology).
3. Returns an interpretable mathematical equation (not a black-box prediction).
4. Visualizes the result as a 3D structure or formula in the browser.

# State of the Field

Several open-source tools exist for symbolic regression and scientific law discovery, but each has significant limitations:

- **PySR (Cranmer, 2020):** A popular symbolic regression library, but it is Python-only and lacks a graphical interface. It must be run locally and is not accessible from a mobile device.
- **SINDy (Brunton, 2016):** A powerful method for discovering dynamical systems, but it requires time-series data and does not support static datasets or 3D visualization.
- **AI Feynman (Udrescu & Tegmark, 2020):** Excellent for discovering physics equations, but limited to low-dimensional data (typically ≤ 15D) and not designed for high-dimensional or noisy real-world datasets.
- **XGBoost / Random Forest:** These provide high predictive accuracy but are black-box models. They cannot produce interpretable equations, making them unsuitable for scientific discovery or regulatory approval.

Elen-k Health OS addresses these limitations by:
1. Providing a **web-based interface** accessible from any device (including mobile).
2. Supporting **both low-dimensional (interpretable equations) and high-dimensional (ensemble predictions)** regimes.
3. Integrating **3D visualization** for molecular structures.
4. Separating the **open-source interface** from **proprietary external engines**, ensuring reproducibility even when the underlying algorithms are closed-source.

# Software Design

The architecture consists of three layers:
- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Framer Motion. Hosted on Vercel. Installable as PWA.
- **Backend:** FastAPI (Python) bridging the frontend to external scientific engines. Handles routing, data validation, and response formatting.
- **Database:** Neon PostgreSQL for storing molecular structures, simulation runs, and user sessions (via Drizzle ORM).

When a user submits data, the platform:
1. Validates the format (CSV/JSON).
2. Calls the appropriate external engine via REST API.
3. Stores the result (equation + confidence + metadata) in the database.
4. Renders the formula or 3D structure in the browser using `3dmol.js`.

All open-source components ship under the MIT license. External scientific engines (such as the proprietary Elen-t symbolic regression engine) are reached through documented REST endpoints, ensuring the interface remains fully reproducible even when the underlying algorithms are proprietary.

# Validation and Use Cases

To demonstrate the platform's capability as a general-purpose scientific orchestration layer, we validated it against three distinct use cases:

**1. High-Dimensional Law Discovery (128D):** The platform successfully orchestrated a proprietary symbolic regression engine on 100 complex drug datasets with 128 descriptors. The external engine achieved a mean R² of 0.82, demonstrating the platform's ability to dispatch, ingest, and visualize high-dimensional results.

**2. Ultra-High-Dimensional Discovery (1024D):** On a 1024-dimensional structured dataset, the platform retrieved an R² of 0.9993 from the external engine, confirming its fitness for extreme-dimensional scientific problems.

**3. DNA Nanotechnology Visualization:** The platform generated, stored, and rendered multiple 3D DNA nanostructures (480-atom DNA Origami Cube, 1200-atom DNA Icosahedron) using `3dmol.js`, demonstrating its 3D visualization capabilities.

# AI Usage Disclosure

Generative AI tools were used **only as assistive tools** during the development of Elen-k Health OS. The following specific uses are disclosed:

**Tools used:**
- Claude (Anthropic) – for drafting frontend UI components (React/Next.js) and documentation.
- ChatGPT (OpenAI) – for brainstorming architectural patterns and code review suggestions.

**Scope of AI assistance:**
- **Frontend code:** AI assisted in generating boilerplate code for the Next.js interface, Tailwind CSS styling, and Framer Motion animations. All AI-generated code was reviewed, tested, and refactored by the author.
- **Documentation:** AI assisted in drafting the README.md and the initial version of this paper. All technical claims, benchmark results, and architectural descriptions were verified by the author.
- **No AI was used** for the core scientific algorithms (the Elen-t symbolic regression engine, the Hybrid Orchestrator, or the Mathematical Ensemble). These components were designed and implemented entirely by the author.

**Human oversight:**
The author (Sadegh Karami Chofteh) has **fully reviewed, edited, and validated** all AI-generated outputs. The core design decisions—including the choice of the hybrid architecture, the benchmark methodology, and the validation strategy—were made by the author. The author takes full responsibility for the accuracy and originality of the final software and manuscript.

**AI disclosure statement:**
This project complies with the JOSS AI usage policy (2026 update). No AI tool was used to autonomously generate the core scientific contributions of this work.

# Acknowledgements

The author thanks the open-source community for the tools that made this project possible: Next.js, FastAPI, React, Tailwind CSS, Framer Motion, 3Dmol.js, and scikit-learn. Special thanks to the developers of PySR and SINDy for their foundational work in symbolic regression and sparse identification, which inspired the design of the Elen-t engine.

This work was supported by the author's independent research. No external funding was received.

# References

- Cranmer, M. (2020). PySR: Fast & Parallelized Symbolic Regression in Python. *Journal of Open Source Software*, 5(52), 2554. https://doi.org/10.21105/joss.02554
- Brunton, S. L., Proctor, J. L., & Kutz, J. N. (2016). Discovering governing equations from data by sparse identification of nonlinear dynamical systems. *Proceedings of the National Academy of Sciences*, 113(15), 3932-3937. https://doi.org/10.1073/pnas.1517384113
- Udrescu, S. M., & Tegmark, M. (2020). AI Feynman: A physics-inspired method for symbolic regression. *Science Advances*, 6(16), eaay2631. https://doi.org/10.1126/sciadv.aay2631
- Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785-794. https://doi.org/10.1145/2939672.2939785
- Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5-32. https://doi.org/10.1023/A:1010933404324
- Rego, N., & Koes, D. (2015). 3Dmol.js: molecular visualization with WebGL. *Bioinformatics*, 31(8), 1322-1324. https://doi.org/10.1093/bioinformatics/btu829

# Availability

Elen-k Health OS is distributed under the MIT license.

- **Repository:** https://github.com/sadegh6811-tech/elen-t8888
- **Live Demo:** https://elen-k56.vercel.app
- **Documentation:** `README.md`
