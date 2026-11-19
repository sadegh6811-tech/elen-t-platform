import { NextResponse } from 'next/server';

const VERCEL_API = 'https://api.vercel.com';

function checkAuth(req: Request): boolean {
  const authHeader = req.headers.get('authorization') || '';
  return authHeader.replace('Bearer ', '') === process.env.DEPLOY_BOT_SECRET;
}

async function findProject(vercelToken: string, target: string) {
  const res = await fetch(`${VERCEL_API}/v9/projects`, {
    headers: { Authorization: `Bearer ${vercelToken}` },
  });
  const data = await res.json();
  return data.projects?.find((p: any) =>
    p.name === target || p.alias?.some((a: any) => a.domain.includes(target))
  );
}

export async function POST(req: Request) {
  try {
    if (!checkAuth(req)) {
      return NextResponse.json({ success: false, error: 'Unauthorized' }, { status: 401 });
    }

    const vercelToken = process.env.VERCEL_TOKEN;
    if (!vercelToken) {
      return NextResponse.json({ success: false, error: 'VERCEL_TOKEN is not set' }, { status: 500 });
    }

    const body = await req.json();
    const { action, targets, env_vars, repo_id } = body;

    // --- عملیات اتصال به گیت ---
    if (action === 'connect_git' && targets && repo_id) {
      const results = [];
      for (const target of targets) {
        const project = await findProject(vercelToken, target);
        if (!project) {
          results.push({ target, success: false, error: 'Project not found' });
          continue;
        }

        const linkRes = await fetch(`${VERCEL_API}/v9/projects/${project.id}/link`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${vercelToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'github',
            repoId: repo_id,
            org: 'sadegh6811-tech',
            repo: 'elen-t-platform'
          }),
        });

        if (linkRes.ok) {
          results.push({ target, success: true, message: 'Git repository connected' });
        } else {
          const errData = await linkRes.json();
          results.push({ target, success: false, error: errData.error?.message });
        }
      }
      return NextResponse.json({ success: true, message: 'Connect Git operation completed', results });
    }

    // --- عملیات بیلد (Deploy) ---
    if (!targets || !Array.isArray(targets) || targets.length === 0) {
      return NextResponse.json({ success: false, error: 'targets array is required' }, { status: 400 });
    }

    const results: any[] = [];
    for (const target of targets) {
      const project = await findProject(vercelToken, target);
      if (!project) {
        results.push({ target, success: false, error: 'Project not found' });
        continue;
      }

      if (env_vars && Object.keys(env_vars).length > 0) {
        for (const [key, value] of Object.entries(env_vars)) {
          await fetch(`${VERCEL_API}/v9/projects/${project.id}/env`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${vercelToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ key, value, target: ['production', 'preview', 'development'], type: 'encrypted' }),
          });
        }
      }

      const deployRes = await fetch(`${VERCEL_API}/v13/deployments`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${vercelToken}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: project.name,
          project: project.id,
          target: 'production',
          gitSource: { type: 'github', repoId: repo_id, ref: 'main' },
        }),
      });

      const deployData = await deployRes.json();
      if (deployRes.ok) {
        results.push({ target, success: true, deployment_id: deployData.id, url: `https://${deployData.url}` });
      } else {
        results.push({ target, success: false, error: deployData.error?.message });
      }
    }

    return NextResponse.json({ success: true, message: 'Operation completed', results });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
