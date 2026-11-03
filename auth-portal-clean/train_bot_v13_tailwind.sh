#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - V13 (Tailwind & PostCSS Fixer)
# ==========================================================

echo "🎓 شروع آموزش ربات (V13) - نصب پکیج‌های Tailwind..."

cd ~/Nazi/auth-portal || { echo "❌ پوشه پیدا نشد"; exit 1; }

# ۱. افزودن پکیج‌های Tailwind به package.json
echo "📦 اضافه کردن Tailwind به لیست وابستگی‌ها..."
npm pkg set devDependencies.tailwindcss="^3.4.1"
npm pkg set devDependencies.postcss="^8.4.38"
npm pkg set devDependencies.autoprefixer="^10.4.19"

# ۲. ساخت فایل تنظیمات Tailwind
echo "⚙️ ساخت tailwind.config.js..."
cat << 'TW' > tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
TW

# ۳. ساخت فایل تنظیمات PostCSS
echo "⚙️ ساخت postcss.config.js..."
cat << 'PC' > postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
PC

# ۴. ارسال به ورسل (با فلگ --force برای پاک کردن کش قبلی)
echo "🚀 ارسال به Vercel (این بار با Tailwind)..."
vercel --prod --yes --force > deploy_result.log 2>&1 || true

# ۵. بررسی نتیجه
if grep -q "Error" deploy_result.log; then
    echo "❌ ورسل باز هم خطا داد! در حال استخراج لاگ‌های جدید..."
    DEPLOY_URL=$(grep -o 'https://auth-portal-[a-z0-9]*-sadegh6811.vercel.app' deploy_result.log | head -n 1)
    if [ -n "$DEPLOY_URL" ]; then
        vercel inspect "$DEPLOY_URL" --logs 2>&1 | grep -i -B 2 -A 5 "error" | tail -n 20
    else
        cat deploy_result.log
    fi
    exit 1
else
    echo "🏆 پیروزی نهایی! سایت با موفقیت در سرور Vercel بیلد و دیپلوی شد."
    grep -E "Production|Aliased" deploy_result.log
fi
