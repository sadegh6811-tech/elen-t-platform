import { NextResponse } from "next/server";
import { db } from "@/db";
import { molecularStructures } from "@/db/schema";
import { eq } from "drizzle-orm";

export async function POST(req: Request) {
  try {
    const { sequence, pdbContent } = await req.json();
    if (!sequence || !pdbContent) {
      return NextResponse.json({ error: "Missing sequence or pdb" }, { status: 400 });
    }

    const pdbId = `DNA_${sequence.slice(0, 6)}`;
    
    // ذخیره در دیتابیس (برای نمایش در Lab)
    await db.insert(molecularStructures).values({
      pdbId,
      name: `Designed DNA (${sequence.length} nt)`,
      classification: "DNA NANOTECH DESIGN",
      atomCount: sequence.length * 2,
      residueCount: sequence.length,
      pdbContent,
      isFavorite: true,
    }).onConflictDoNothing();

    return NextResponse.json({ pdbId, success: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
