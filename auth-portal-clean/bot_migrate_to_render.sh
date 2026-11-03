#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - Cloud Migration Module (Render)
# ==========================================================

echo "☁️ ربات آغاز مأموریت انتقال بک‌اند به سرورهای ابری Render..."
sleep 1

cd ~/سبزی || { echo "❌ پوشه سبزی پیدا نشد"; exit 1; }

# ۱. ساخت فایل requirements.txt
echo "📦 مرحله ۱: ساخت لیست پکیج‌های پایتون (requirements.txt)..."
cat << 'REQ' > requirements.txt
fastapi
uvicorn
pandas
requests
python-multipart
pydantic
REQ

# ۲. ساخت فایل render.yaml (دستور ساخت سرور در Render)
echo "⚙️ مرحله ۲: ساخت تنظیمات استقرار (render.yaml)..."
cat << 'YAML' > render.yaml
services:
  - type: web
    name: elen-auth-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn public_proxy:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
YAML

# ۳. آماده‌سازی Git و آپلود به گیت‌هاب
echo "📤 مرحله ۳: آماده‌سازی کدها برای ارسال به GitHub..."
if [ ! -d ".git" ]; then
    git init
    git branch -M main
fi

# ساخت فایل gitignore برای جلوگیری از آپلود فایل‌های اضافی
echo -e "venv/\n__pycache__/\n*.pyc\n.env\nnode_modules/" > .gitignore

git add requirements.txt render.yaml public_proxy.py security_sensor.py security_engine.py .gitignore 2>/dev/null
git commit -m "feat: prepare backend for Render cloud deployment" > /dev/null 2>&1

echo "=========================================================="
echo "🏆 ربات کار خود را تمام کرد! فایل‌ها برای سرور ابری آماده شدند."
echo ""
echo "⚠️ برای تکمیل انتقال، فقط این ۳ قدم کوتاه را انجام دهید:"
echo "۱. کدهای پوشه سبزی را در یک ریپازیتوری (Repository) جدید در GitHub آپلود کنید."
echo "   (دستور: git remote add origin <لینک_گیت_هاب_شما> && git push -u origin main)"
echo ""
echo "۲. به سایت Render.com بروید و اکانت بسازید (رایگان)."
echo "۳. روی New Web Service کلیک کنید و ریپازیتوری گیت‌هاب خود را انتخاب کنید."
echo "   (Render خودش فایل render.yaml را می‌خواند و سرور را روشن می‌کند)."
echo "=========================================================="
