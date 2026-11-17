import { NextResponse } from "next/server";
import { db, pool } from "@/db";

export async function GET() {
  try {
    const res = await pool.query('SELECT 1');
    return NextResponse.json({ success: true, message: "Workspace works" });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
