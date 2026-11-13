import { NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

export async function GET() {
  try {
    const res = await pool.query(
      "SELECT criteria_name, criteria_value, created_at FROM system_telemetry ORDER BY id DESC LIMIT 20"
    );
    
    // مرتب‌سازی داده‌ها برای نمایش در نمودار
    const ramData = res.rows.filter(r => r.criteria_name === 'RAM_PERCENT').reverse();
    const netData = res.rows.filter(r => r.criteria_name === 'NETWORK_PING').reverse();

    return NextResponse.json({ 
      success: true, 
      ram: ramData,
      net: netData
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
