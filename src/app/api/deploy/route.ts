import { NextResponse } from 'next/server';

const VERCEL_API = 'https://api.vercel.com';

// --- ابزار کمکی: بررسی احراز هویت ---
function checkAuth(req: Request): boolean {
  const authHeader = req.headers.get('authorization') || '';
  const token = authHeader.replace('Bearer ', '');
  return token === process.env.DEPLOY_BOT_SECRET;
}

// --- ابزار کمکی: پیدا کردن پروژه با نام یا دامنه ---
async function findProject(vercelToken: string, target: string) {
  const res = await fetch(`${VERCEL_API}/v9/projects`, {
    headers: { Authorization: `Bearer ${vercelToken}` },
  });
  const data = await res.json();
  return data.projects?.find(
    (p: any) =>
      p.name === target ||
      p.alias?.some((a: any) => a.domain.includes(target))
  );
}

// --- POST: تنظیم متغیرها + شروع بیلد ---
export async function POST(req: Request) {
  try {
    if (!checkAuth(req)) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const vercelToken = process.env.VERCEL_TOKEN;
    if (!vercelToken) {
      return NextResponse.json(
        { success: false, error: 'VERCEL_TOKEN is not set' },
        { status: 500 }
      );
    }

    const body = await req.json();
    const { action, targets, env_vars } = body;
    // targets: آرایه‌ای از نام پروژه‌ها (مثلاً ["elen-seven", "elen-k56"])

    if (!targets || !Array.isArray(targets) || targets.length === 0) {
      return NextResponse.json(
        { success: false, error: '`targets` array is required' },
        { status: 400 }
      );
    }

    const results: any[] = [];

    for (const target of targets) {
      const project = await findProject(vercelToken, target);
      if (!project) {
        results.push({ target, success: false, error: 'Project not found' });
        continue;
      }

      // ۱. تنظیم متغیرهای محیطی
      if (env_vars && Object.keys(env_vars).length > 0) {
        for (const [key, value] of Object.entries(env_vars)) {
          const envRes = await fetch(
            `${VERCEL_API}/v9/projects/${project.id}/env`,
            {
              method: 'POST',
              headers: {
                Authorization: `Bearer ${vercelToken}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                key,
                value,
                target: ['production', 'preview', 'development'],
                type: 'encrypted',
              }),
            }
          );
          if (!envRes.ok) {
            const errData = await envRes.json();
            results.push({
              target,
              success: false,
              error: `Env ${key}: ${errData.error?.message}`,
            });
            continue;
          }
        }
      }

      // ۲. شروع بیلد
      const deployRes = await fetch(`${VERCEL_API}/v13/deployments`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${vercelToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: project.name,
          project: project.id,
          target: 'production',
          gitSource: { type: 'github', ref: 'main' },
        }),
      });

      const deployData = await deployRes.json();
      if (!deployRes.ok) {
        results.push({
          target,
          success: false,
          error: deployData.error?.message,
        });
        continue;
      }

      results.push({
        target,
        success: true,
        deployment_id: deployData.id,
        url: `https://${deployData.url}`,
        state: deployData.readyState || 'QUEUED',
      });
    }

    return NextResponse.json({
      success: true,
      message: 'Operation completed',
      action: action || 'deploy',
      results,
    });
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// --- GET: گزارش وضعیت یک بیلد ---
export async function GET(req: Request) {
  try {
    if (!checkAuth(req)) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const vercelToken = process.env.VERCEL_TOKEN;
    if (!vercelToken) {
      return NextResponse.json(
        { success: false, error: 'VERCEL_TOKEN is not set' },
        { status: 500 }
      );
    }

    const url = new URL(req.url);
    const deploymentId = url.searchParams.get('id');
    const action = url.searchParams.get('action'); // rollback

    // حالت Rollback
    if (action === 'rollback' && deploymentId) {
      const res = await fetch(
        `${VERCEL_API}/v9/projects/${deploymentId}/rollback`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${vercelToken}` },
        }
      );
      const data = await res.json();
      return NextResponse.json({ success: res.ok, data });
    }

    // حالت Status
    if (!deploymentId) {
      return NextResponse.json(
        { success: false, error: '`id` query param is required' },
        { status: 400 }
      );
    }

    const res = await fetch(`${VERCEL_API}/v13/deployments/${deploymentId}`, {
      headers: { Authorization: `Bearer ${vercelToken}` },
    });
    const data = await res.json();

    return NextResponse.json({
      success: res.ok,
      id: data.id,
      state: data.readyState,
      url: data.url ? `https://${data.url}` : null,
      createdAt: data.createdAt,
      buildingAt: data.buildingAt,
      ready: data.ready,
    });
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
