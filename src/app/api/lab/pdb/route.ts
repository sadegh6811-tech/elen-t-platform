import { NextResponse } from 'next/server';
import { db } from '../../../../db';
import { molecularStructures } from '../../../../db/schema';
import { eq } from 'drizzle-orm';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const id = searchParams.get('id');
  if (!id) return NextResponse.json({ error: 'Missing ID' }, { status: 400 });

  try {
    const [record] = await db.select().from(molecularStructures).where(eq(molecularStructures.pdbId, id));

    // 👇 شرط اصلاح شد: فقط اگر خطی با ATOM شروع شود
    if (record && record.pdbContent && /^ATOM/m.test(record.pdbContent)) {
      return NextResponse.json({
        pdbId: record.pdbId,
        name: record.name || 'Unknown',
        atomCount: record.atomCount || 0,
        pdbData: record.pdbContent
      });
    }

    if (id.length === 4) {
      const rcsbRes = await fetch(`https://files.rcsb.org/download/${id}.pdb`, { cache: 'no-store' });
      
      if (rcsbRes.ok) {
        const pdbText = await rcsbRes.text();
        const atomCount = (pdbText.match(/^ATOM/gm) || []).length;
        
        // اگر دیتای دریافتی معتبر بود (اتم داشت)
        if (atomCount > 0) {
            try {
              // 👇 از onConflictDoUpdate استفاده می‌کنیم تا دیتای خراب قبلی را با دیتای کامل جایگزین کند
              await db.insert(molecularStructures).values({
                pdbId: id,
                name: 'RCSB Structure',
                atomCount: atomCount,
                pdbContent: pdbText
              }).onConflictDoUpdate({
                target: molecularStructures.pdbId,
                set: { pdbContent: pdbText, atomCount: atomCount }
              });
            } catch(e) { console.error('DB Save error:', e); }

            return NextResponse.json({
              pdbId: id,
              name: 'RCSB Structure',
              atomCount: atomCount,
              pdbData: pdbText
            });
        }
      }
    }

    return NextResponse.json({ error: 'Structure not found or incomplete' }, { status: 404 });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
