import { NextResponse } from "next/server";

const VALID_AA = /^[ACDEFGHIKLMNPQRSTVWY]+$/i;

export async function POST(request: Request) {
  try {
    const { sequence } = await request.json();

    if (typeof sequence !== "string") {
      return NextResponse.json({ success: false, error: "Sequence must be a string." }, { status: 400 });
    }

    const cleanSeq = sequence.trim().toUpperCase();

    if (cleanSeq.length < 10) {
      return NextResponse.json({ success: false, error: "Sequence must be at least 10 amino acids." }, { status: 400 });
    }

    if (cleanSeq.length > 400) {
      return NextResponse.json({ success: false, error: "Sequence too long. ESMFold free tier allows up to 400 residues." }, { status: 400 });
    }

    if (!VALID_AA.test(cleanSeq)) {
      return NextResponse.json({ success: false, error: "Invalid characters. Only standard amino acids allowed." }, { status: 400 });
    }

    const response = await fetch("https://api.esmatlas.com/foldSequence/v1/pdb/", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: cleanSeq,
    });

    if (!response.ok) {
      const errText = await response.text().catch(() => "");
      return NextResponse.json({ success: false, error: `ESMFold API error (${response.status}): ${errText.slice(0, 200)}` }, { status: response.status });
    }

    const pdbData = await response.text();

    if (!pdbData.includes("ATOM")) {
      return NextResponse.json({ success: false, error: "Invalid PDB response from ESMFold." }, { status: 502 });
    }

    return NextResponse.json({
      success: true,
      pdb: pdbData,
      length: cleanSeq.length,
      residues: (pdbData.match(/^ATOM/gm) || []).length,
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message || "Unknown error" }, { status: 500 });
  }
}
