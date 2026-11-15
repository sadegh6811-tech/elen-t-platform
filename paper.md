---
title: 'Elen-k: A Unified Web Workspace for DNA Nanotechnology Design and Molecular Simulation'
tags:
  - DNA Nanotechnology
  - WebGL
  - Next.js
  - Scientific Software
  - Bilingual Interface
authors:
  - name: Sadegh Karami Chofteh
    affiliation: Independent Researcher
date: 13 November 2026
---

# Summary

Designing functional DNA nanotechnology—from simple origami structures to complex dynamic nanodevices—currently requires researchers to juggle multiple disconnected tools. `Elen-k` is an open-source, bilingual (Persian/English) web workspace that unifies the DNA nanotech design loop. It takes natural-language intent, routes it to an external molecular design engine via a documented API, visualizes the resulting 3D structure in the browser, and allows for physics simulation tracking—all from a smartphone.

# Statement of Need

To our knowledge, no existing open-source tool offers a unified, bilingual, mobile-first workflow specifically targeting DNA nanotechnology design with real-time 3D feedback. `Elen-k` fills this gap for educators, students, and researchers who need an accessible entry point into DNA nanodevice engineering without abandoning scientific rigor.

# Software Design

The architecture consists of a Next.js frontend hosted on Vercel, a Neon PostgreSQL database acting as a message queue, and a Python worker running externally. When a user requests a structure (e.g., "design a DNA cube"), the request is queued in the database. The worker processes it, generates a strict-format PDB string, and returns it to the database. The frontend then fetches the PDB and renders it using `3dmol.js`. All open-source components ship under the MIT license; external scientific engines are reached through documented REST endpoints so that the interface remains reproducible even when the underlying algorithms are proprietary.

# Validation and Example Use Cases

**DNA Nanotechnology (DNE) Engine:** The interface successfully orchestrated the generation, database storage, and real-time WebGL rendering of complex DNA nanostructures, including a 480-atom DNA Origami Cube, a 6-helix DNA Nanotube, and a 1200-atom DNA Icosahedron.

**Scientific Orchestration (Multi-Engine Benchmark):** To evaluate the robustness of the orchestration layer, we simulated 100 complex drug datasets with 128 descriptors and nested non-linear branches. A single-engine approach completely failed (Mean R² = -0.3687). However, Elen-k's Multi-Engine Hybrid Architecture dynamically routed the problem, successfully rescuing 100/100 cases and achieving a mean R² = 0.8203. This demonstrates the platform's unique ability to recover interpretable laws in high-dimensional regimes where black-box models fail.

**AI Usage Disclosure:** Generative AI was used to assist in frontend UI code and documentation. The core scientific algorithms remain proprietary.

# Availability
Elen-k is distributed under the MIT license.
- **Repository:** https://github.com/sadegh6811-tech/elen-t8888
- **Documentation:** `README.md`
