# Elen-k — Unified Workspace & DNA Nanotech Engine (DNE)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![Deploy on Vercel](https://img.shields.io/badge/Deploy-Vercel-black)](https://vercel.com)

A bilingual (Persian/English), browser-based AI workspace for **DNA nanotechnology design**, **molecular visualization**, and **symbolic scientific discovery**.

## 🚀 Key Feature: AI-Driven DNA Nanotech Engine (DNE)
Users can design complex DNA nanostructures (e.g., Origami Cubes) simply by typing a natural language prompt (e.g., *"یک تراشه DNA مکعبی طراحی کن"*).
1. The request is processed by a proprietary symbolic-regression router.
2. A Python engine generates a strict-format PDB file.
3. The structure is saved to a Neon PostgreSQL database.
4. The frontend automatically navigates to the Lab tab and renders the 3D molecular structure via `3dmol.js`.

## Architecture
- **Frontend:** Next.js 16, React 19, Tailwind CSS, `3dmol.js`.
- **Database:** Neon (PostgreSQL) with Drizzle ORM.
- **Worker:** Python running on Termux (Android) / external servers.
- **Deploy-bot:** Built-in serverless endpoint for zero-touch Vercel deployments.

## Quick Start
1. Clone the repo: `git clone https://github.com/sadegh6811-tech/elen-t8888.git`
2. Install dependencies: `npm install --legacy-peer-deps`
3. Set up `.env.local` with your `DATABASE_URL` and `VERCEL_TOKEN`.
4. Run: `npm run dev`

## License
MIT
