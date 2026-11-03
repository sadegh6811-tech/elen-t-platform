#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - V12 (Deep Log Extractor & Cleaner)
# ==========================================================

PROJECT_DIR=~/Nazi/auth-portal
PINGGY_URL="https://oedaa-37-187-56-56.run.pinggy-free.link"

echo "🎓 شروع آموزش ربات (V12) - استخراج لاگ‌های عمیق..."

cd $PROJECT_DIR || { echo "❌ پوشه پیدا نشد"; exit 1; }

# ۱. پاکسازی کامل و حذف فایل‌های پیکربندی اضافی
# حذف vercel.json باعث می‌شود ورسل از تنظیمات پیش‌فرض خودش (Zero-Config) استفاده کند
rm -rf node_modules dist .vercel package-lock.json vercel.json .vercelignore
echo "🧹 محیط به حالت صفر (Zero-Config) بازگشت."

# ۲. بازنویسی package.json با وابستگی‌های حداقلی و تست‌شده
cat << 'PKG' > package.json
{
  "name": "elen-auth-portal",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.2.0",
    "typescript": "^5.2.2"
  }
}
PKG

# ۳. تنظیم لینک بک‌اند
echo "$PINGGY_URL" | vercel env add VITE_API_URL production --force > /dev/null 2>&1 || true

# ۴. ارسال به ورسل (با فلگ --debug برای دریافت لاگ‌های بیشتر)
echo "🚀 در حال ارسال به Vercel (با حالت Debug)..."
vercel --prod --yes --debug > deploy_debug.log 2>&1 || true

# ۵. بررسی نتیجه و استخراج لاگ‌های دقیق
if grep -q "Error: Command" deploy_debug.log; then
    echo "❌ ورسل در بیلد خطا داد. در حال استخراج لاگ‌های واقعی سرور..."
    
    # پیدا کردن لینک دیپلوی از لاگ
    DEPLOY_URL=$(grep -o 'https://auth-portal-[a-z0-9]*-sadegh6811.vercel.app' deploy_debug.log | head -n 1)
    
    if [ -n "$DEPLOY_URL" ]; then
        echo "🔍 دریافت لاگ‌های دقیق از: $DEPLOY_URL"
        echo "=================================================="
        # گرفتن لاگ‌های عمیق و فیلتر کردن خطوط خطا
        vercel inspect "$DEPLOY_URL" --logs 2>&1 | grep -i -B 2 -A 10 "error" | tail -n 30
        echo "=================================================="
        echo "💡 راهنما: خطوط بالا دقیقاً می‌گویند کدام فایل یا ماژول مشکل دارد."
    else
        echo "⚠️ لینک دیپلوی پیدا نشد. لاگ خام در حال بررسی است:"
        tail -n 30 deploy_debug.log
    fi
    exit 1
else
    echo "🏆 پیروزی! بیلد در سرور ورسل با موفقیت انجام شد."
    grep -E "Production|Aliased" deploy_debug.log
fi
