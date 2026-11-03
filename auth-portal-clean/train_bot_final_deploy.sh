#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - Final Auto-Deploy & Env Fixer
# ==========================================================

PINGGY_URL="https://gvtag-37-46-119-215.run.pinggy-free.link"
PROJECT_DIR=~/Nazi/auth-portal

echo "🎓 ربات مأموریت نهایی را آغاز می‌کند..."

cd $PROJECT_DIR || { echo "❌ پوشه پیدا نشد"; exit 1; }

# ۱. پاکسازی توکن خراب و متغیرهای قبلی
echo "🧹 پاکسازی تنظیمات قبلی..."
unset VERCEL_TOKEN
vercel env rm VITE_API_URL production --yes > /dev/null 2>&1

# ۲. تزریق لینک جدید Pinggy
echo "🔗 تزریق لینک جدید بک‌اند به Vercel..."
echo "$PINGGY_URL" | vercel env add VITE_API_URL production > /dev/null 2>&1

# ۳. دیپلوی نهایی روی Vercel
echo "🚀 ارسال نهایی به Vercel (لطفاً صبر کنید)..."
vercel --prod --yes --force > deploy_final.log 2>&1

# ۴. بررسی نتیجه
if grep -q "Ready in" deploy_final.log; then
    echo "🏆 پیروزی! سایت با موفقیت با لینک جدید دیپلوی شد."
    grep -E "Production|Aliased" deploy_final.log
    echo ""
    echo "⚠️ نکته بسیار مهم:"
    echo "به داشبورد Vercel بروید و در بخش Settings -> Deployment Protection،"
    echo "گزینه Vercel Authentication را روی Disabled قرار دهید تا سایت برای مرورگر باز شود."
else
    echo "❌ خطا در دیپلوی. لاگ‌ها:"
    tail -n 20 deploy_final.log
fi
