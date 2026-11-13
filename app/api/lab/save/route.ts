import { NextResponse } from 'next/server';
import { Client } from 'pg';

export async function POST(req: Request) {
  try {
    const { id, name, pdbData } = await req.json();
    if (!id || !pdbData) {
      return NextResponse.json({ error: 'Missing fields' }, { status: 400 });
    }

    const client = new Client({
      connectionString: process.env.DATABASE_URL,
      ssl: { rejectUnauthorized: false }
    });

    await client.connect();
    
    // استفاده از نام دقیق ستون‌ها: pdb_id و pdb_content
    const query = `
      INSERT INTO molecular_structures (pdb_id, name, pdb_content) 
      VALUES ($1, $2, $3)
      ON CONFLICT (pdb_id) DO UPDATE SET pdb_content = EXCLUDED.pdb_content;
    `;
    
    await client.query(query, [id, name, pdbData]);
    await client.end();

    return NextResponse.json({ success: true, message: "Saved successfully to Neon!" });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
