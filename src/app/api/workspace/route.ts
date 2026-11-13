import { NextRequest, NextResponse } from "next/server";
import { db, pool } from "@/db";
import { aiMessages, terminalHistory, workspaceDeployments } from "@/db/schema";
import { ensureWorkspaceSeeded } from "@/db/seed";
import { eq } from "drizzle-orm";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  try {
    const jobId = request.nextUrl.searchParams.get("jobId");
    if (jobId) {
      const result = await pool.query(`SELECT status, result FROM engine_jobs WHERE id = $1`, [Number(jobId)]);
      return NextResponse.json(result.rows[0] || {});
    }
    await ensureWorkspaceSeeded();
    const [deployments, terminal, messages] = await Promise.all([
      db.select().from(workspaceDeployments).orderBy(workspaceDeployments.id),
      db.select().from(terminalHistory).orderBy(terminalHistory.id).limit(40),
      db.select().from(aiMessages).orderBy(aiMessages.id).limit(40),
    ]);
    return NextResponse.json({ deployments, terminal, messages });
  } catch (error) {
    return NextResponse.json({ error: "Failed to load." }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const action = String(body?.action || "");

    // 🧹 اکشن جدید برای پاک کردن چت
    if (action === "clear_ai") {
      await db.delete(aiMessages);
      return NextResponse.json({ success: true });
    }

    if (action === "deploy") {
      const id = Number(body?.id);
      await pool.query(`INSERT INTO engine_jobs (command, status) VALUES ($1, 'pending')`, ["[RUN_DEPLOY]"]);
      const nextHash = Math.random().toString(16).slice(2, 9);
      const [updated] = await db.update(workspaceDeployments).set({ status: "live", commitHash: nextHash, updatedAt: new Date() }).where(eq(workspaceDeployments.id, id)).returning();
      return NextResponse.json({ deployment: updated });
    }

    if (action === "toggle_deploy") {
      const id = Number(body?.id);
      const [existing] = await db.select().from(workspaceDeployments).where(eq(workspaceDeployments.id, id)).limit(1);
      if (!existing) return NextResponse.json({ error: "Not found" }, { status: 404 });
      const nextStatus = existing.status === "live" ? "standby" : "live";
      const [updated] = await db.update(workspaceDeployments).set({ status: nextStatus, updatedAt: new Date() }).where(eq(workspaceDeployments.id, id)).returning();
      return NextResponse.json({ deployment: updated });
    }

    if (action === "terminal") {
      const command = String(body?.command || "").trim();
      const activePdb = String(body?.activePdb || "1CRN").toUpperCase();
      const output = `termux@elen-k:~$ '${command}' -> exit 0 (target: ${activePdb})`;
      const [entry] = await db.insert(terminalHistory).values({ command, output }).returning();
      return NextResponse.json({ entry });
    }

    if (action === "ai") {
      const prompt = String(body?.prompt || "").trim();
      const contextPdb = String(body?.contextPdb || "1CRN").toUpperCase();
      if (!prompt) return NextResponse.json({ error: "Empty prompt" }, { status: 400 });

      const [userMsg] = await db.insert(aiMessages).values({ role: "user", content: prompt, contextPdb }).returning();

      const jobResult = await pool.query(`INSERT INTO engine_jobs (command, status) VALUES ($1, 'pending') RETURNING id`, [`chat:${prompt}`]);
      const jobId = jobResult.rows[0].id;

      const replyText = "⏳ در حال پردازش در موتور Elen-t... لطفاً چند لحظه صبر کنید. نتیجه به‌زودی به‌روزرسانی می‌شود.";
      const [aiMsg] = await db.insert(aiMessages).values({ role: "assistant", content: replyText, contextPdb }).returning();

      return NextResponse.json({ userMsg, aiMsg, jobId });
    }

    return NextResponse.json({ error: "Unsupported action" }, { status: 400 });
  } catch (error) {
    return NextResponse.json({ error: "Failed to process." }, { status: 500 });
  }
}
