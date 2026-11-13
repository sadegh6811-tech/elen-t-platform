import { NextResponse } from 'next/server';
import { db } from '@/src/db';
import { sql } from 'drizzle-orm';

export async function POST(req: Request) {
  try {
    const { id, name, pdbData } = await req.json();
    if (!id || !pdbData) {
      return NextResponse.json({ error: 'Missing fields' }, { status: 400 });
    }

    await db.execute(sql`
      INSERT INTO molecular_structures (id, name, pdb_data)
      VALUES (${id}, ${name}, ${pdbData})
      ON CONFLICT (id) DO UPDATE SET pdb_data = EXCLUDED.pdb_data;
    `);

    return NextResponse.json({ success: true, message: "Saved successfully to Neon!" });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
