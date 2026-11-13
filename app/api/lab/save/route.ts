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
    
    const query = `
      INSERT INTO molecular_structures (id, name, pdb_data)
      VALUES ($1, $2, $3)
      ON CONFLICT (id) DO UPDATE SET pdb_data = EXCLUDED.pdb_data;
    `;
    
    await client.query(query, [id, name, pdbData]);
    await client.end();

    return NextResponse.json({ success: true, message: "Saved successfully to Neon!" });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
