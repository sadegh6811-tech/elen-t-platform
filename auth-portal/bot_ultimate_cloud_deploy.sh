#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - Ultimate Cloud Auto-Deploy (V3)
# ==========================================================

echo "☁️ ربات: آغاز فرآیند استقرار ابری کامل (کاملاً خودکار)..."
sleep 1

# ۱. پیدا کردن توکن گیت‌هاب
TOKEN_PATH="$HOME/.github_token"
if [ -f "$TOKEN_PATH" ]; then
    GITHUB_TOKEN=$(cat "$TOKEN_PATH" | tr -d '\n\r ')
    echo "✅ توکن گیت‌هاب با موفقیت از گوشی خوانده شد."
else
    echo "❌ فایل .github_token در پوشه اصلی پیدا نشد."
    echo "لطفاً مطمئن شوید این فایل در مسیر ~ وجود دارد."
    exit 1
fi

# ۲. پیدا کردن نام کاربری گیت‌هاب
echo "🕵️‍♂️ در حال پیدا کردن نام کاربری گیت‌هاب..."
USERNAME=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | grep '"login":' | cut -d'"' -f4)

if [ -z "$USERNAME" ]; then
    echo "❌ توکن گیت‌هاب نامعتبر است یا منقضی شده است."
    exit 1
fi
echo "👤 نام کاربری: $USERNAME"

# ۳. رفتن به پوشه سبزی و آماده‌سازی فایل‌ها
cd ~/سبزی || { echo "❌ پوشه سبزی پیدا نشد"; exit 1; }

# ساخت فایل‌های مورد نیاز Render
echo "📦 ساخت فایل‌های استقرار (requirements.txt, render.yaml)..."
echo -e "fastapi\nuvicorn\npandas\nrequests\npython-multipart\npydantic" > requirements.txt

cat << 'YAML' > render.yaml
services:
  - type: web
    name: elen-auth-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn public_proxy:app --host 0.0.0.0 --port $PORT
YAML

echo -e "venv/\n__pycache__/\n*.pyc\n.env\nnode_modules/" > .gitignore

# ۴. ساخت مخزن در گیت‌هاب (اگر وجود نداشته باشد)
REPO_NAME="elen-backend-cloud"
echo "🐙 در حال ساخت مخزن در گیت‌هاب..."
curl -s -H "Authorization: token $GITHUB_TOKEN" \
     -d "{\"name\":\"$REPO_NAME\", \"private\": false}" \
     https://api.github.com/user/repos > /dev/null

# ۵. آپلود کدها به گیت‌هاب
echo "🚀 در حال ارسال کدها به گیت‌هاب (این ممکن است کمی طول بکشد)..."
git config --global user.name "ELEN Deploy Bot"
git config --global user.email "bot@elen.com"

if [ ! -d ".git" ]; then
    git init
fi
git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "https://$GITHUB_TOKEN@github.com/$USERNAME/$REPO_NAME.git"

git add requirements.txt render.yaml public_proxy.py security_sensor.py security_engine.py .gitignore
git commit -m "Auto-deploy: Prepare ELEN backend for Render" > /dev/null 2>&1
git push -u origin main -f > push_log.txt 2>&1

if grep -q "main -> main" push_log.txt || [ $? -eq 0 ]; then
    echo "🏆 پیروزی! کدها با موفقیت در گیت‌هاب آپلود شدند."
    echo "=========================================================="
    echo "🎯 آخرین مأموریت برای شما (فقط ۱ دقیقه):"
    echo "۱. به سایت render.com بروید و با گیت‌هاب لاگین کنید."
    echo "۲. روی New + کلیک کرده و Web Service را انتخاب کنید."
    echo "۳. ریپازیتوری '$REPO_NAME' را انتخاب کنید."
    echo "۴. Render خودش فایل render.yaml را می‌خواند. فقط روی Create Web Service کلیک کنید."
    echo "=========================================================="
    echo "💡 بعد از ساخت، Render یک لینک (مثل https://...onrender.com) به شما می‌دهد."
    echo "آن لینک را کپی کنید و برای من بفرستید تا سایت را به آن وصل کنم."
else
    echo "❌ خطا در ارسال به گیت‌هاب. لاگ:"
    cat push_log.txt
fi
