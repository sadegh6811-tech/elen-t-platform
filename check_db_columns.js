const fs = require('fs');
const path = require('path');
const { Client } = require('pg');

const envPath = path.join(__dirname, '.env.local');
const envContent = fs.readFileSync(envPath, 'utf8');
const dbUrl = envContent.match(/DATABASE_URL=(.*)/)[1].trim();

const client = new Client({
  connectionString: dbUrl,
  ssl: { rejectUnauthorized: false }
});

async function check() {
  try {
    await client.connect();
    console.log("✅ متصل به دیتابیس شد.");
    
    // دریافت لیست ستون‌های جدول
    const res = await client.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'molecular_structures';
    `);
    
    console.log("📋 ستون‌های جدول molecular_structures:");
    console.table(res.rows);
    
  } catch (err) {
    console.error("❌ خطا:", err.message);
  } finally {
    await client.end();
  }
}

check();
