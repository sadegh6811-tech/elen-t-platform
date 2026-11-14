import { NextResponse } from 'next/server';
import { db } from '../../../../db';
import { molecularStructures } from '../../../../db/schema';
import { eq } from 'drizzle-orm';

export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const id = searchParams.get('id');
  if (!id) return NextResponse.json({ error: 'Missing ID' }, { status: 400 });

  try {
    // 1. اگر ساختار سفارشی DNA باشد (مثل DNA_HELIX_01) از دیتابیس می‌خوانیم
    if (id.startsWith('DNA_')) {
      const [record] = await db.select().from(molecularStructures).where(eq(molecularStructures.pdbId, id));
      if (record && record.pdbContent) {
        return NextResponse.json({
          pdbId: record.pdbId,
          name: record.name || 'Unknown',
          atomCount: record.atomCount || 0,
          pdbData: record.pdbContent
        });
      }
      return NextResponse.json({ error: 'DNA structure not found in DB' }, { status: 404 });
    }

    // 2. اگر کد استاندارد PDB (۴ حرفی) باشد، مستقیماً از سرور RCSB دانلود می‌کنیم (بدون چک کردن دیتابیس)
    if (id.length === 4) {
      const rcsbRes = await fetch(`https://files.rcsb.org/download/${id.toUpperCase()}.pdb`, {
        cache: 'no-store',
        headers: { 'Pragma': 'no-cache', 'Cache-Control': 'no-cache' }
      });

      if (rcsbRes.ok) {
        const pdbText = await rcsbRes.text();
        
        if (pdbText.length > 1000) {
           const atomCount = (pdbText.match(/^ATOM/gm) || []).length;
           
           // آپدیت کردن دیتابیس با دیتای صحیح (برای بارهای بعدی)
           try {
             await db.insert(molecularStructures).values({
                pdbId: id.toUpperCase(),
                name: 'RCSB Structure',
                atomCount: atomCount,
                pdbContent: pdbText
              }).onConflictDoUpdate({
                target: molecularStructures.pdbId,
                set: { pdbContent: pdbText, atomCount: atomCount }
              });
           } catch(e) { console.error('DB Save error:', e); }

           return NextResponse.json({
              pdbId: id.toUpperCase(),
              name: 'RCSB Structure',
              atomCount: atomCount,
              pdbData: pdbText
           });
        }
      }
    }

    return NextResponse.json({ error: 'Structure not found or invalid' }, { status: 404 });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
