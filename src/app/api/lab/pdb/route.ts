import { NextResponse } from "next/server";
import { db } from "@/db";
import { molecularStructures } from "@/db/schema";
import { eq } from "drizzle-orm";
import { parsePdbMetadata, FALLBACK_1CRN_PDB } from "@/lib/pdbUtils";

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const pdbId = (searchParams.get("id") || "").toUpperCase();
    if (!pdbId || pdbId.length < 4) return NextResponse.json({ error: "Invalid ID" }, { status: 400 });
    const cached = await db.select().from(molecularStructures).where(eq(molecularStructures.pdbId, pdbId)).limit(1);
    if (cached[0]) {
      const meta = parsePdbMetadata(cached[0].pdbContent, pdbId);
      return NextResponse.json({ ...meta, pdbData: cached[0].pdbContent, source: "cache" });
    }
    let pdbContent = FALLBACK_1CRN_PDB;
    if (pdbId !== "1CRN") {
      try {
        const res = await fetch(`https://files.rcsb.org/download/${pdbId}.pdb`, { signal: AbortSignal.timeout(5000) });
        if (res.ok) pdbContent = await res.text();
        else return NextResponse.json({ error: `PDB ${pdbId} not found` }, { status: 404 });
      } catch { return NextResponse.json({ error: `Failed to fetch ${pdbId}` }, { status: 502 }); }
    }
    const meta = parsePdbMetadata(pdbContent, pdbId);
    await db.insert(molecularStructures).values({ pdbId, name: meta.name, classification: meta.classification, atomCount: meta.atomCount, residueCount: meta.residueCount, pdbContent }).onConflictDoNothing();
    return NextResponse.json({ ...meta, pdbData: pdbContent, source: "rcsb" });
  } catch (error) {
    return NextResponse.json({ error: "Server error" }, { status: 500 });
  }
}
