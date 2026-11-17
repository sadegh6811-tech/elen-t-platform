import { drizzle } from "drizzle-orm/neon-http";
import { neon } from "@neondatabase/serverless";
import * as schema from "./schema";

if (!process.env.DATABASE_URL) {
  throw new Error("❌ DATABASE_URL is not set. Check your .env.local file.");
}

export const sql = neon(process.env.DATABASE_URL);
export const db = drizzle(sql, { schema });

// شبیه‌ساز pool برای فایل‌هایی که هنوز از روش قدیمی استفاده می‌کنند
export const pool = {
  query: async (text: string, params: any[] = []) => {
    try {
      // استفاده از sql.unsafe برای اجرای کوئری‌های خام در neon-http
      const rows = await (sql as any).unsafe(text, params);
      return { rows };
    } catch (e) {
      console.error("Database query error:", e);
      throw e;
    }
  }
};
