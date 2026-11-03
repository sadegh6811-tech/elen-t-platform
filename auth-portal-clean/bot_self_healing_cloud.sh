#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - V4 (Self-Healing Cloud Deploy)
# ==========================================================

echo "☁️ ربات: آغاز فرآیند استقرار ابری (هوشمند)..."
sleep 1

# ۱. بررسی توکن قبلی
TOKEN_PATH="$HOME/.github_token"
VALID_TOKEN=""

if [ -f "$TOKEN_PATH" ]; then
    OLD_TOKEN=$(cat "$TOKEN_PATH" | tr -d '\n\r ')
    # تست اعتبار توکن
    RESPONSE=$(curl -s -H "Authorization: token $OLD_TOKEN" https://api.github.com/user)
    if echo "$RESPONSE" | grep -q '"login"'; then
        VALID_TOKEN="$OLD_TOKEN"
        echo "✅ توکن قبلی معتبر است. استفاده می‌شود..."
    fi
fi

# ۲. اگر توکن معتبر نبود، از کاربر می‌پرسد
while [ -z "$VALID_TOKEN" ]; do
    echo "----------------------------------------------------------"
    echo "⚠️ توکن قبلی نامعتبر یا منقضی شده است."
    echo "لطفاً یک توکن جدید از گیت‌هاب بسازید (Settings -> Developer settings -> Tokens -> Generate new token -> تیک repo)."
    read -p "🔑 لطفاً توکن جدید گیت‌هاب را پیست کنید و Enter بزنید: " NEW_TOKEN
    
    if [ -z "$NEW_TOKEN" ]; then
        echo "❌ شما هیچ توکنی وارد نکردید! دوباره تلاش کنید."
        continue
    fi

    # تست توکن جدید
    RESPONSE=$(curl -s -H "Authorization: token $NEW_TOKEN" https://api.github.com/user)
    if echo "$RESPONSE" | grep -q '"login"'; then
        VALID_TOKEN="$NEW_TOKEN"
        echo "$VALID_TOKEN" > "$TOKEN_PATH"
        echo "✅ توکن جدید تایید شد و در گوشی ذخیره شد."
    else
        echo "❌ توکن وارد شده معتبر نیست! لطفاً دوباره امتحان کنید."
    fi
done

# ۳. پیدا کردن نام کاربری گیت‌هاب
echo "🕵️‍♂️ در حال پیدا کردن نام کاربری گیت‌هاب..."
USERNAME=$(curl -s -H "Authorization: token $VALID_TOKEN" https://api.github.com/user | grep '"login":' | cut -d'"' -f4)
echo "👤 نام کاربری: $USERNAME"

# ۴. آماده‌سازی فایل‌های سبزی
cd ~/سبزی || { echo "❌ پوشه سبزی پیدا نشد"; exit 1; }

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

# ۵. ساخت مخزن در گیت‌هاب
REPO_NAME="elen-backend-cloud"
echo "🐙 در حال ساخت مخزن در گیت‌هاب..."
curl -s -H "Authorization: token $VALID_TOKEN" \
     -d "{\"name\":\"$REPO_NAME\", \"private\": false}" \
     https://api.github.com/user/repos > /dev/null

# ۶. آپلود کدها به گیت‌هاب
echo "🚀 در حال ارسال کدها به گیت‌هاب (این ممکن است کمی طول بکشد)..."
git config --global user.name "ELEN Deploy Bot"
git config --global user.email "bot@elen.com"

if [ ! -d ".git" ]; then
    git init
fi
git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "https://$VALID_TOKEN@github.com/$USERNAME/$REPO_NAME.git"

git add requirements.txt render.yaml public_proxy.py security_sensor.py security_engine.py .gitignore
git commit -m "Auto-deploy: Prepare ELEN backend for Render" > /dev/null 2>&1
git push -u origin main -f > push_log.txt 2>&1

if grep -q "main -> main" push_log.txt || [ $? -eq 0 ]; then
    echo "🏆 پیروزی! کدها با موفقیت در گیت‌هاب آپلود شدند."
    echo "=========================================================="
    echo "🎯 مأموریت شما (فقط ۱ دقیقه):"
    echo "۱. به سایت render.com بروید و با گیت‌هاب لاگین کنید."
    echo "۲. روی New + کلیک کرده و Web Service را انتخاب کنید."
    echo "۳. ریپازیتوری '$REPO_NAME' را انتخاب کنید."
    echo "۴. فقط روی Create Web Service کلیک کنید."
    echo "=========================================================="
    echo "💡 بعد از ساخت، Render یک لینک (مثل https://...onrender.com) به شما می‌دهد."
    echo "آن لینک را کپی کنید و برای من بفرستید."
else
    echo "❌ خطا در ارسال به گیت‌هاب. لاگ:"
    cat push_log.txt
fi
