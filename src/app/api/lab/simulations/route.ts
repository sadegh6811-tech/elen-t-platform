import { NextResponse } from "next/server";
import { db } from "@/db";
import { simulationRuns } from "@/db/schema";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { pdbId, representation, temperature, durationNs, energyKcalMol, rmsdAngstrom, logs } = body;
    const run = await db.insert(simulationRuns).values({ pdbId, representation, temperature, durationNs: durationNs || 50, energyKcalMol, rmsdAngstrom, logs, status: "completed" }).returning();
    return NextResponse.json({ run: run[0] });
  } catch (error) {
    return NextResponse.json({ error: "Failed" }, { status: 500 });
  }
}
