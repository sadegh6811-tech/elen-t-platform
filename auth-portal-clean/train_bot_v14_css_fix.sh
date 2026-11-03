#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - V14 (Tailwind V3 CSS Fixer)
# ==========================================================

echo "🎓 شروع آموزش ربات (V14) - اصلاح فایل CSS برای Tailwind V3..."

cd ~/Nazi/auth-portal || { echo "❌ پوشه پیدا نشد"; exit 1; }

# ۱. بازنویسی فایل index.css با دستورات استاندارد نسخه ۳
echo "📝 بازنویسی src/index.css..."
cat << 'CSS' > src/index.css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: system-ui, -apple-system, sans-serif;
  background-color: #0B0A1A;
  color: white;
}
CSS

# ۲. اطمینان از تنظیمات استاندارد PostCSS
echo "⚙️ بررسی postcss.config.js..."
cat << 'PC' > postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
PC

# ۳. ارسال به ورسل با فلگ force برای پاک کردن کش
echo "🚀 ارسال نهایی به Vercel..."
vercel --prod --yes --force > deploy_final.log 2>&1 || true

# ۴. بررسی نتیجه
if grep -q "Error" deploy_final.log; then
    echo "❌ ورسل باز هم خطا داد! استخراج لاگ نهایی:"
    DEPLOY_URL=$(grep -o 'https://auth-portal-[a-z0-9]*-sadegh6811.vercel.app' deploy_final.log | head -n 1)
    if [ -n "$DEPLOY_URL" ]; then
        vercel inspect "$DEPLOY_URL" --logs 2>&1 | grep -i -B 2 -A 5 "error" | tail -n 20
    else
        tail -n 20 deploy_final.log
    fi
    exit 1
else
    echo "🏆🏆🏆 پیروزی کامل! سایت شما با تمام استایل‌های تیلویند در سرور Vercel بیلد و دیپلوی شد."
    grep -E "Production|Aliased" deploy_final.log
fi
