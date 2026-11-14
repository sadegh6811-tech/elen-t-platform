const fs = require('fs');
const path = require('path');

const pdbData = fs.readFileSync(path.join(process.env.HOME, 'dna_tetrahedron.pdb'), 'utf8');

async function upload() {
  try {
    console.log("⏳ در حال ارسال به Vercel...");
    // آدرس سایت خود را اینجا قرار دهید
    const response = await fetch('https://elen-k56.vercel.app/api/lab/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: 'DNA_TETRA_01',
        name: 'DNA Tetrahedron',
        pdbData: pdbData
      })
    });

    const data = await response.json();
    if (response.ok) {
      console.log("🎉 موفقیت:", data.message);
    } else {
      console.error("❌ خطا از سمت سرور:", data.error);
    }
  } catch (error) {
    console.error("❌ خطای شبکه:", error.message);
  }
}

upload();
