import { NextRequest, NextResponse } from "next/server";
import { Pool } from "pg";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      return NextResponse.json({ success: false, error: "No file provided" }, { status: 400 });
    }

    if (!file.name.endsWith(".csv")) {
      return NextResponse.json({ success: false, error: "Only .csv files allowed" }, { status: 400 });
    }
    if (file.size > 2 * 1024 * 1024) {
      return NextResponse.json({ success: false, error: "File too large (max 2MB)" }, { status: 413 });
    }

    const content = await file.text();
    const rowCount = content.trim().split("\n").length - 1;

    const result = await pool.query(
      `INSERT INTO uploaded_files (filename, file_content, row_count, status)
       VALUES ($1, $2, $3, 'pending') RETURNING id, filename, row_count`,
      [file.name, content, rowCount]
    );

    await pool.query(
      `INSERT INTO engine_jobs (command, status) VALUES ($1, 'pending')`,
      [`[FILE_UPLOAD] id=${result.rows[0].id} | filename=${file.name} | rows=${rowCount} | Please analyze this dataset and find the formula.`]
    );

    return NextResponse.json({
      success: true,
      file: result.rows[0],
      message: "File uploaded and queued for Elen-t analysis.",
    });
  } catch (err: any) {
    return NextResponse.json({ success: false, error: err.message }, { status: 500 });
  }
}

export async function GET() {
  try {
    const result = await pool.query(
      `SELECT id, filename, row_count, status, uploaded_at
       FROM uploaded_files ORDER BY uploaded_at DESC LIMIT 20`
    );
    return NextResponse.json({ success: true, files: result.rows });
  } catch (err: any) {
    return NextResponse.json({ success: false, error: err.message }, { status: 500 });
  }
}
