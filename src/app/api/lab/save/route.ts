import { NextResponse } from "next/server";
import { db, sql } from "@/db";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    return NextResponse.json({ success: true, message: "Lab Save works (Neon HTTP)" });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
