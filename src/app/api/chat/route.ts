import { NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

export async function POST(request: Request) {
  try {
    const { message } = await request.json();
    const command = `chat:${message}`;

    const insertRes = await pool.query(
      "INSERT INTO engine_jobs (command) VALUES ($1) RETURNING id",
      [command]
    );
    const jobId = insertRes.rows[0].id;

    let attempts = 0;
    let reply = "";
    
    // ⏳ افزایش تایم‌اوت به ۱۲۰ ثانیه (برای موتورهای سنگین)
    while (attempts < 300) { 
      await new Promise(resolve => setTimeout(resolve, 1000)); 
      
      const checkRes = await pool.query(
        "SELECT status, result FROM engine_jobs WHERE id = $1",
        [jobId]
      );
      
      const job = checkRes.rows[0];
      if (job.status === 'done') {
        reply = job.result;
        break;
      } else if (job.status === 'failed') {
        throw new Error(job.result || "Engine failed to process the message.");
      }
      attempts++;
    }

    if (!reply) throw new Error("Timeout: Engine did not respond in time.");

    return NextResponse.json({ success: true, reply });

  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

// 📜 GET endpoint to fetch chat history
export async function GET() {
  try {
    const result = await pool.query(
      "SELECT role, content, created_at FROM chat_history WHERE session_id = 'default' ORDER BY created_at ASC LIMIT 50"
    );
    return NextResponse.json({ success: true, messages: result.rows });
  } catch (err: any) {
    return NextResponse.json({ success: false, error: err.message }, { status: 500 });
  }
}
