import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { action, target, env_vars } = body;
    
    const vercelToken = process.env.VERCEL_TOKEN;
    if (!vercelToken) {
      return NextResponse.json({ success: false, error: "VERCEL_TOKEN is not set in environment variables." }, { status: 500 });
    }

    let projectId = null;

    // ۱. تنظیم متغیرهای محیطی (در صورت ارسال)
    if (env_vars && Object.keys(env_vars).length > 0) {
      const projectsRes = await fetch('https://api.vercel.com/v9/projects', {
        headers: { Authorization: `Bearer ${vercelToken}` },
      });
      const projectsData = await projectsRes.json();
      
      const project = projectsData.projects?.find((p: any) => 
        p.name === target || p.alias?.some((a: any) => a.domain.includes(target))
      );

      if (!project) {
        return NextResponse.json({ success: false, error: `Project '${target}' not found` }, { status: 404 });
      }
      
      projectId = project.id;

      for (const [key, value] of Object.entries(env_vars)) {
        const envRes = await fetch(`https://api.vercel.com/v9/projects/${projectId}/env`, {
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
        });

        if (!envRes.ok) {
          const errData = await envRes.json();
          return NextResponse.json({ success: false, error: `Failed to set env: ${errData.error?.message}` }, { status: 500 });
        }
      }
    }

    // ۲. شروع بیلد
    const deployRes = await fetch('https://api.vercel.com/v13/deployments', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${vercelToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: target || 'elen',
        project: target || 'elen',
        target: 'production',
        gitSource: { type: 'github', ref: 'main' },
      }),
    });

    const deployData = await deployRes.json();

    if (!deployRes.ok) {
      return NextResponse.json({ success: false, error: deployData.error?.message }, { status: 500 });
    }

    return NextResponse.json({
      success: true,
      message: "Deployment & Env setup triggered successfully!",
      project: target,
      deployment_id: deployData.id,
      url: `https://${deployData.url}`,
    });

  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
