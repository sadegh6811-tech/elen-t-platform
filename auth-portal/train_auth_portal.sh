#!/data/data/com.termux/files/usr/bin/bash
# ==========================================
# 🧠 ELEN Deploy-Bot - Advanced Training Module
# Target: auth-portal (Vite/React)
# ==========================================

echo "🎓 اجرای ماژول آموزش پیشرفته برای auth-portal..."

# ۱. رفتن به پوشه درست (حتی اگر کاربر جای دیگری باشد)
cd ~/Nazi/auth-portal || { echo "❌ پوشه پروژه پیدا نشد"; exit 1; }

# ۲. تنظیم متغیر محیطی برای اجبار به بیلد در سرور (حل مشکل ARM64)
export VERCEL_FORCE_SERVER_BUILD=1

# ۳. بررسی وجود فایل .env (برای اتصال به Pinggy)
if [ ! -f .env ]; then
    echo "⚠️ هشدار: فایل .env وجود ندارد! لینک Pinggy را تنظیم کنید."
else
    echo "✅ فایل .env پیدا شد. لینک API: $(cat .env | cut -d '=' -f 2)"
fi

# ۴. پاکسازی فایل‌های اضافی برای جلوگیری از خطای Rollup
rm -rf node_modules dist .vercel

# ۵. اجرای دیپلوی با تمام تنظیمات ایمن
echo "🚀 شروع دیپلوی هوشمند..."
vercel --prod --yes

echo "🎉 آموزش با موفقیت اجرا شد و دیپلوی انجام گردید."
