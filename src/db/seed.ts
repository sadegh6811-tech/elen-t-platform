import { db } from "@/db";
import { aiMessages, molecularStructures, simulationRuns, terminalHistory, workspaceDeployments } from "@/db/schema";
import { FALLBACK_1CRN_PDB, parsePdbMetadata } from "@/lib/pdbUtils";
import { count } from "drizzle-orm";

let seededPromise: Promise<void> | null = null;

export async function ensureWorkspaceSeeded() {
  if (!seededPromise) {
    seededPromise = runSeed().catch((err) => { seededPromise = null; throw err; });
  }
  return seededPromise;
}

async function runSeed() {
  const [{ value: deployCount }] = await db.select({ value: count() }).from(workspaceDeployments);
  if (deployCount === 0) {
    await db.insert(workspaceDeployments).values([
      { serviceName: "elenk-quantum-md-worker", branch: "main", environment: "qpu-cluster-01", status: "live", commitHash: "9f42c1e" },
      { serviceName: "rcsb-pdb-gateway", branch: "prod/v4", environment: "edge-mesh-asia", status: "live", commitHash: "3a8b7d0" },
      { serviceName: "amber-forcefield-gpu", branch: "feat/cuda-12.6", environment: "termux-bridge", status: "standby", commitHash: "e19d04a" },
    ]);
  }

  const [{ value: termCount }] = await db.select({ value: count() }).from(terminalHistory);
  if (termCount === 0) {
    await db.insert(terminalHistory).values([
      { command: "elenk-boot --profile quantum-lab", output: "[OK] Elen-k Kernel v4.2.9\n[OK] WebGL2 / 3Dmol Renderer attached\n[OK] Connected to PostgreSQL" },
      { command: "pdb-status --default 1CRN", output: "PDB_ID: 1CRN (Crambin) · Source: RCSB PDB" },
    ]);
  }

  const [{ value: aiCount }] = await db.select({ value: count() }).from(aiMessages);
  if (aiCount === 0) {
    await db.insert(aiMessages).values([
      { role: "assistant", contextPdb: "1CRN", content: "Elen-k.Ai Quantum Copilot online. Currently synchronized with PDB 1CRN." },
    ]);
  }

  const [{ value: simCount }] = await db.select({ value: count() }).from(simulationRuns);
  if (simCount === 0) {
    await db.insert(simulationRuns).values([
      { pdbId: "1CRN", representation: "cartoon", temperature: 300, durationNs: 50, status: "completed", energyKcalMol: "-1482.4 kcal/mol", rmsdAngstrom: "0.94 Å", logs: ["[00:00.1] Initializing AMBER-Q9..."] },
    ]);
  }

  const [{ value: molCount }] = await db.select({ value: count() }).from(molecularStructures);
  if (molCount === 0) {
    const meta = parsePdbMetadata(FALLBACK_1CRN_PDB, "1CRN");
    await db.insert(molecularStructures).values({
      pdbId: "1CRN", name: meta.name, classification: meta.classification,
      atomCount: meta.atomCount, residueCount: meta.residueCount,
      pdbContent: FALLBACK_1CRN_PDB, isFavorite: true,
    }).onConflictDoNothing();
  }
}
