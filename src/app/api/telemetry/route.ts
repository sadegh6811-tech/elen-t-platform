import { NextResponse } from "next/server";
import { db, sql } from "@/db";

export async function GET() {
  try {
    const res = await (sql as any).query('SELECT * FROM telemetry LIMIT 10');
    // اضافه کردن تایپ :any به r برای رفع خطای TypeScript
    const ramData = res.rows?.filter((r: any) => r.criteria_name === 'RAM_PERCENT').reverse() || [];
    const netData = res.rows?.filter((r: any) => r.criteria_name === 'NETWORK_PING').reverse() || [];
    
    return NextResponse.json({ ramData, netData });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
