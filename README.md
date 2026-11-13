# Elen-k — Unified Workspace & DNE Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![Deploy on Vercel](https://img.shields.io/badge/Deploy-Vercel-black)](https://vercel.com)

A bilingual (Persian/English), browser-based workspace for **DNA nanotechnology design**, **molecular visualization**, and **symbolic scientific discovery**.

## What it does

Elen-k unifies the fragmented scientific workflow into a single 5-tab dashboard:

| Tab | Purpose |
|-----|---------|
| **Monitor** | Live telemetry from the worker |
| **Deploy-bot** | Trigger remote builds and deployments |
| **Lab** | 3D molecular viewer + DNA Origami designer |
| **Termux** | Live Termux (Android) shell bridge |
| **Elen-k.Ai** | Natural-language scientific assistant |

The **DNA Nanotech Engine (DNE)** generates standard PDB structures (DNA cubes, lattices, tetrahedrons) from raw sequence data and renders them in-browser using `3dmol.js`.

## Why it matters

Designing DNA nanodevices usually means juggling caDNAno + PyMOL + a separate simulation stack. Elen-k collapses that into **one browser tab**, works on **mobile (Termux)** and **desktop**, and supports **Persian + English** with proper RTL.

## Quick Start

### Prerequisites

- Node.js 20+
- A [Neon](https://neon.tech) Postgres database (free tier works)
- (Optional, for backend) Python 3.10+ on Termux or any Linux

### Install & Run

```bash
git clone https://github.com/sadegh6811-tech/elen-t8888.git
cd elen-t8888
npm install --legacy-peer-deps
