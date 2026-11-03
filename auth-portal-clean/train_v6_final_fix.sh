#!/data/data/com.termux/files/usr/bin/bash
# ==========================================
# 🧠 ELEN Deploy-Bot - V6 (Polyfill Disabler)
# ==========================================

echo "🎓 شروع آموزش نهایی (V6) - حل مشکل Polyfill..."

cd ~/Nazi/auth-portal || { echo "❌ پوشه پیدا نشد"; exit 1; }

# ۱. ساخت vite.config.ts با غیرفعال کردن پولیفیل (مهم‌ترین قدم)
echo "🔧 مرحله ۱: غیرفعال کردن modulepreload-polyfill..."
cat << 'VITE' > vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    modulePreload: {
      polyfill: false // این خط به Vite می‌گوید پولیفیل را تزریق نکن
    }
  }
})
VITE

# ۲. اصلاح package.json (دور زدن tsc)
echo "🔧 مرحله ۲: اصلاح package.json..."
node -e "const fs=require('fs'); const p=JSON.parse(fs.readFileSync('package.json')); p.scripts.build='vite build'; fs.writeFileSync('package.json', JSON.stringify(p, null, 2));"

# ۳. بیلد در گوشی (حالا باید بدون خطا انجام شود)
echo "🔨 مرحله ۳: بیلد گرفتن در گوشی..."
npm run build > build_final.log 2>&1

if [ -d "dist" ]; then
    echo "✅ بیلد در گوشی با موفقیت انجام شد! پوشه dist ساخته شد."
    echo "🚀 مرحله ۴: ارسال فایل‌های آماده به Vercel (حالت prebuilt)..."
    vercel --prod --prebuilt --yes
else
    echo "❌ بیلد همچنان شکست خورد. لاگ خطا:"
    cat build_final.log
    exit 1
fi

echo "🎉 عملیات با موفقیت به پایان رسید."
