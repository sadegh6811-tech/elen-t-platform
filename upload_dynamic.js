const fs = require('fs');
const path = require('path');
const pdbData = fs.readFileSync(path.join(process.env.HOME, 'dna_dynamic_box.pdb'), 'utf8');

async function upload() {
  console.log("⏳ ارسال جعبه پویای DNA به Vercel...");
  const res = await fetch('https://elen-k56.vercel.app/api/lab/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        id: 'DNA_BOX_OPEN_01', 
        name: 'Dynamic DNA Nanobox (Hinged)', 
        pdbData: pdbData 
    })
  });
  const data = await res.json();
  console.log(res.ok ? "🎉 موفقیت: " + data.message : "❌ خطا: " + data.error);
}
upload();
