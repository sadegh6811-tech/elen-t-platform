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

# Availability

Elen-k Health OS is distributed under the MIT license.

- **Repository:** https://github.com/sadegh6811-tech/elen-t8888
- **Live Demo:** https://elen-k56.vercel.app
- **Documentation:** `README.md`
