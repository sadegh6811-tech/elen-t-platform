#!/data/data/com.termux/files/usr/bin/bash
# ==========================================
# 🤖 ELEN Deploy-Bot - Smart Cloud Build Module
# ==========================================

# ۱. توقف در صورت بروز خطا
set -e

echo "🧠 فعال‌سازی منطق دیپلوی ابری (Cloud Build)..."

# ۲. ورود به پوشه پروژه
cd ~/Nazi/auth-portal || { echo "❌ پوشه پیدا نشد"; exit 1; }

# ۳. پاکسازی فایل‌های خراب‌کننده (جلوگیری از آپلود فایل‌های ARM64 به ورسل)
echo "🧹 پاکسازی فایل‌های محلی..."
rm -rf node_modules dist package-lock.json .vercel

# ۴. ساخت فایل .vercelignore برای جلوگیری از آپلود فایل‌های اضافی
echo "🛡️ ساخت سپر محافظ (.vercelignore)..."
cat << 'IGNORE' > .vercelignore
node_modules
dist
package-lock.json
.env
IGNORE

# ۵. اطمینان از استاندارد بودن package.json
cat << 'PKG' > package.json
{
  "name": "elen-auth-portal",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.66",
    "@types/react-dom": "^18.2.22",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.2.2",
    "vite": "^5.2.0"
  }
}
PKG

# ۶. قرار دادن متغیر محیطی (لینک Pinggy) به صورت مستقیم در تنظیمات ورسل
# این کار باعث می‌شود حتی اگر فایل .env آپلود نشود، سایت به بک‌اند وصل باشد
echo "🔗 تنظیم لینک بک‌اند در ورسل..."
echo "https://oedaa-37-187-56-56.run.pinggy-free.link" | vercel env add VITE_API_URL production --force > /dev/null 2>&1 || true

# ۷. ارسال به ورسل با اجبار به بیلد در سرور (بدون دخالت گوشی)
echo "🚀 ارسال به Vercel و اجبار به بیلد در سرور..."
vercel --prod --yes --force

echo "🎉 عملیات دیپلوی ابری با موفقیت به پایان رسید."
