import { NextResponse } from "next/server";
import { db, sql } from "@/db";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    // جایگزینی برای کوئری قدیمی
    const result = await (sql as any).query('SELECT 1'); 
    return NextResponse.json({ success: true, message: "Chat API works (Neon HTTP)" });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
