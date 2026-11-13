import { NextResponse } from 'next/server';

export async function POST() {
  try {
    const token = process.env.VERCEL_TOKEN;
    
    if (!token) {
      return NextResponse.json({ error: 'VERCEL_TOKEN not configured in Vercel Environment Variables' }, { status: 500 });
    }

    const response = await fetch('https://api.vercel.com/v13/deployments', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: 'elen', 
        gitSource: {
          type: 'github',
          repoId: 'sadegh6811-tech/elen-t8888',
          ref: 'main',
        },
      }),
    });

    const data = await response.json();
    
    if (!response.ok) throw new Error(data.error?.message || 'Deploy failed');

    return NextResponse.json({ success: true, message: "Deployment triggered successfully!" });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
