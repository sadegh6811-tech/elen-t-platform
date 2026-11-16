import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const token = process.env.VERCEL_TOKEN;
    
    if (!token) {
      return NextResponse.json({ error: 'VERCEL_TOKEN not configured' }, { status: 500 });
    }

    let body: any = {};
    try {
      body = await req.json();
    } catch {}

    const projectName = body.project_name || 'elen';
    const branch = body.branch || 'main';
    const repoOrg = body.org || 'sadegh6811-tech';
    const repoName = body.repo || 'elen-t8888';

    const response = await fetch('https://api.vercel.com/v13/deployments', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: projectName,
        gitSource: {
          type: 'github',
          org: repoOrg,
          repo: repoName,
          ref: branch,
        },
      }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      return NextResponse.json(
        { success: false, error: data.error?.message || 'Deploy failed', details: data },
        { status: response.status }
      );
    }

    return NextResponse.json({ 
      success: true, 
      message: "Deployment triggered successfully!",
      project: projectName,
      branch: branch,
      deployment_id: data.id,
      url: `https://${data.url || data.alias?.[0] || 'check-dashboard'}`,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
