import { NextResponse } from 'next/server';
import { Client } from 'pg';

export async function POST(req: Request) {
  try {
    const { id, name, pdbData } = await req.json();
    if (!id || !pdbData) {
      return NextResponse.json({ error: 'Missing fields' }, { status: 400 });
    }

    // شمارش خودکار اتم‌ها
    const atomCount = (pdbData.match(/^ATOM/gm) || []).length;

    const client = new Client({
      connectionString: process.env.DATABASE_URL,
      ssl: { rejectUnauthorized: false }
    });

    await client.connect();
    
    // آپدیت دیتابیس با احتساب atomCount
    const query = `
      INSERT INTO molecular_structures (pdb_id, name, pdb_content, atom_count) 
      VALUES ($1, $2, $3, $4)
      ON CONFLICT (pdb_id) DO UPDATE SET 
        pdb_content = EXCLUDED.pdb_content,
        atom_count = EXCLUDED.atom_count;
    `;
    
    await client.query(query, [id, name, pdbData, atomCount]);
    await client.end();

    return NextResponse.json({ success: true, message: `Saved! (${atomCount} atoms)` });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
