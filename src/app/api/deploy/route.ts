import { NextResponse } from "next/server";
import { Pool } from "pg";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

export async function POST() {
  try {
    // ارسال دستور به جدول engine_jobs
    await pool.query(
      `INSERT INTO engine_jobs (command, status) VALUES ($1, 'pending')`,
      ["[RUN_DEPLOY]"]
    );
    return NextResponse.json({ success: true, message: "Deploy command queued." });
  } catch (err: any) {
    return NextResponse.json({ success: false, error: err.message }, { status: 500 });
  }
}
