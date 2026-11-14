import { NextResponse } from 'next/server';
import { db } from '@/src/db';
import { molecularStructures } from '@/src/db/schema';
import { eq } from 'drizzle-orm';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const id = searchParams.get('id');
  if (!id) return NextResponse.json({ error: 'Missing ID' }, { status: 400 });

  try {
    // 1. جستجو در دیتابیس
    const [record] = await db.select().from(molecularStructures).where(eq(molecularStructures.pdbId, id));

    // اگر در دیتابیس بود و شامل خطوط ATOM بود، همان را برگردان
    if (record && record.pdbContent && record.pdbContent.includes('ATOM')) {
      return NextResponse.json({
        pdbId: record.pdbId,
        name: record.name || 'Unknown',
        atomCount: record.atomCount || 0,
        pdbData: record.pdbContent
      });
    }

    // 2. اگر در دیتابیس نبود یا ناقص بود (مثل 1CRN)، مستقیماً از RCSB دانلود کن
    if (id.length === 4) {
      const rcsbRes = await fetch(`https://files.rcsb.org/download/${id}.pdb`);
      if (rcsbRes.ok) {
        const pdbText = await rcsbRes.text();
        const atomCount = (pdbText.match(/^ATOM/gm) || []).length;
        
        // ذخیره در دیتابیس برای استفاده‌های بعدی
        try {
          await db.insert(molecularStructures).values({
            pdbId: id,
            name: 'RCSB Structure',
            atomCount: atomCount,
            pdbContent: pdbText
          }).onConflictDoNothing();
        } catch(e) { console.error('DB Save error:', e); }

        return NextResponse.json({
          pdbId: id,
          name: 'RCSB Structure',
          atomCount: atomCount,
          pdbData: pdbText
        });
      }
    }

    return NextResponse.json({ error: 'Structure not found or invalid' }, { status: 404 });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
