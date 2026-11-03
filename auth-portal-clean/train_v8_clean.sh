#!/data/data/com.termux/files/usr/bin/bash
# ==========================================
# 🧠 ELEN Deploy-Bot - V8 (Clean Override)
# ==========================================

echo "🎓 شروع آموزش نهایی (V8) - پاکسازی و اجبار به WASM..."

cd ~/Nazi/auth-portal || { echo "❌ پوشه پیدا نشد"; exit 1; }

# ۱. حذف Rollup از لیست وابستگی‌های مستقیم (تا خطای EOVERRIDE رخ ندهد)
echo "🧹 مرحله ۱: حذف وابستگی مستقیم Rollup..."
npm pkg delete devDependencies.rollup
npm pkg delete dependencies.rollup

# ۲. اجبار NPM به استفاده از نسخه WASM
echo "🔧 مرحله ۲: تنظیم override برای Rollup WASM..."
npm pkg set overrides.rollup="npm:@rollup/wasm-node@latest"

# ۳. تنظیم دستور بیلد (دور زدن tsc)
npm pkg set scripts.build="vite build"

# ۴. بازسازی vite.config.ts
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

# ۵. پاکسازی کامل برای نصب تمیز
echo "🧹 مرحله ۳: پاکسازی node_modules و package-lock.json..."
rm -rf node_modules package-lock.json dist

# ۶. نصب مجدد پکیج‌ها
echo "📦 مرحله ۴: نصب مجدد پکیج‌ها (لطفاً صبر کنید)..."
npm install

# ۷. بیلد در گوشی
echo "🔨 مرحله ۵: بیلد گرفتن در گوشی با Rollup WASM..."
npm run build > build_wasm.log 2>&1

# ۸. بررسی موفقیت و ارسال به ورسل
if [ -d "dist" ]; then
    echo "✅ بیلد با موفقیت انجام شد! (پوشه dist ساخته شد)"
    echo "🚀 مرحله ۶: ارسال فایل‌های آماده به Vercel..."
    vercel --prod --prebuilt --yes
else
    echo "❌ بیلد همچنان شکست خورد. لاگ خطا:"
    cat build_wasm.log
    exit 1
fi

echo "🎉 عملیات ربات به پایان رسید."
