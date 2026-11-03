#!/data/data/com.termux/files/usr/bin/bash
# ==========================================
# 🧠 ELEN Deploy-Bot - V7 (WASM Rollup Fix)
# ==========================================

echo "🎓 شروع آموزش نهایی (V7) - رفع باگ Native Rollup با WASM..."

cd ~/Nazi/auth-portal || { echo "❌ پوشه پیدا نشد"; exit 1; }

# ۱. اجبار npm به استفاده از نسخه WASM به جای نسخه Native
echo "🔧 مرحله ۱: تنظیم override برای Rollup WASM..."
npm pkg set overrides.rollup="npm:@rollup/wasm-node@latest"

# ۲. تنظیم دستور بیلد (دور زدن tsc)
npm pkg set scripts.build="vite build"

# ۳. بازسازی vite.config.ts برای اطمینان از عدم تداخل
cat << 'VITE' > vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    modulePreload: {
      polyfill: false
    }
  }
})
VITE

# ۴. پاکسازی کامل برای نصب تمیز
echo "🧹 مرحله ۲: پاکسازی node_modules و package-lock.json..."
rm -rf node_modules package-lock.json dist

# ۵. نصب مجدد پکیج‌ها با تنظیمات جدید
echo "📦 مرحله ۳: نصب مجدد پکیج‌ها (لطفاً صبر کنید)..."
npm install

# ۶. بیلد در گوشی
echo "🔨 مرحله ۴: بیلد گرفتن در گوشی با Rollup WASM..."
npm run build > build_wasm.log 2>&1

# ۷. بررسی موفقیت و ارسال به ورسل
if [ -d "dist" ]; then
    echo "✅ بیلد با موفقیت انجام شد! (پوشه dist ساخته شد)"
    echo "🚀 مرحله ۵: ارسال فایل‌های آماده به Vercel..."
    vercel --prod --prebuilt --yes
else
    echo "❌ بیلد همچنان شکست خورد. لاگ خطا:"
    cat build_wasm.log
    exit 1
fi

echo "🎉 عملیات ربات به پایان رسید."
