const fs = require('fs');
const path = require('path');
const { Client } = require('pg');

const pdbPath = path.join(process.env.HOME, 'dna_tetrahedron.pdb');
const pdbData = fs.readFileSync(pdbPath, 'utf8');

const envPath = path.join(__dirname, '.env.local');
const envContent = fs.readFileSync(envPath, 'utf8');
const dbUrlMatch = envContent.match(/DATABASE_URL=(.*)/);
const dbUrl = dbUrlMatch ? dbUrlMatch[1].trim() : null;

if (!dbUrl) {
    console.error("❌ DATABASE_URL پیدا نشد.");
    process.exit(1);
}

const client = new Client({
  connectionString: dbUrl,
  ssl: { rejectUnauthorized: false },
  connectionTimeoutMillis: 15000, 
  keepAlive: true 
});

async function insertStructure() {
  try {
    console.log("⏳ در حال تلاش برای اتصال به Neon...");
    await client.connect();
    console.log("✅ متصل شد.");
    
    const query = `
      INSERT INTO molecular_structures (id, name, pdb_data) 
      VALUES ($1, $2, $3)
      ON CONFLICT (id) DO UPDATE SET pdb_data = EXCLUDED.pdb_data;
    `;
    
    await client.query(query, ['DNA_TETRA_01', 'DNA Tetrahedron', pdbData]);
    console.log("🎉 ساختار DNA_TETRA_01 با موفقیت در دیتابیس ذخیره شد!");
    
  } catch (err) {
    console.error("❌ خطا:", err.message);
  } finally {
    await client.end();
  }
}

insertStructure();
