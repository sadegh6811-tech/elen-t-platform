#!/bin/bash

echo "=================================================="
echo "🤖 [ربات جامع]: شروع فرآیند اتوماتیک دیپلوی (گیت‌هاب + Render)..."
echo "=================================================="

# --- مرحله ۱: آماده‌سازی فایل‌های پیش‌نیاز ---
echo "🛠️ [۱/۵] آماده‌سازی فایل‌های پیش‌نیاز..."
touch src/components/Karami.tsx
if ! grep -q "pandas" requirements.txt 2>/dev/null; then
    echo "pandas" >> requirements.txt
    echo "✅ کتابخانه pandas به requirements.txt اضافه شد."
fi

# تغییر مخزن مقصد به devstudio-bot (چون Render از این مخزن می‌خواند)
sed -i "s/sadegh6811-tech\/elen-t-platform/sadegh6811-tech\/devstudio-bot/g" activate_security_shield.py 2>/dev/null
echo "✅ تنظیمات اولیه انجام شد."

# --- مرحله ۲: بررسی توکن گیت‌هاب ---
if [ ! -s "$HOME/.github_token" ]; then
    echo "⚠️ توکن گیت‌هاب یافت نشد."
    read -p "🔑 لطفا توکن گیت‌هاب خود (با دسترسی repo) را پیست کنید: " GH_TOKEN
    echo -n "$GH_TOKEN" > "$HOME/.github_token"
    echo "✅ توکن ذخیره شد."
fi

# --- مرحله ۳: آپلود کدها به گیت‌هاب ---
echo "🚀 [۲/۵] در حال تزریق کدها و آپلود به گیت‌هاب..."
python3 activate_security_shield.py

if [ $? -ne 0 ]; then
    echo "❌ خطا در آپلود به گیت‌هاب. (ممکن است اینترنت یا توکن مشکل داشته باشد)."
    exit 1
fi
echo "✅ کدها با موفقیت در گیت‌هاب آپلود شدند."

# --- مرحله ۴: دیپلوی در Render ---
echo "🌐 [۳/۵] در حال ارسال دستور دیپلوی به Render..."
if [ ! -s "$HOME/.render_deploy_hook" ]; then
    echo "⚠️ لینک Deploy Hook یافت نشد."
    echo "لطفاً به داشبورد Render بروید (Settings -> Deploy Hook) و لینک را کپی کنید."
    read -p "🔗 لینک Deploy Hook را اینجا پیست کنید: " RENDER_HOOK
    echo -n "$RENDER_HOOK" > "$HOME/.render_deploy_hook"
fi

HOOK_URL=$(cat "$HOME/.render_deploy_hook")
curl -s -X POST "$HOOK_URL" > /dev/null
echo "✅ دستور دیپلوی به Render ارسال شد. سرور در حال بیلد است..."

# --- مرحله ۵: انتظار و تست نهایی ---
echo "⏳ [۴/۵] صبر برای بیلد شدن در Render (حدود ۶۰ ثانیه)..."
sleep 60

echo "🧪 [۵/۵] تست نهایی سرور برای رویت مسیرهای جدید (Math)..."
MAX_RETRIES=5
COUNT=0
SUCCESS=0

while [ $COUNT -lt $MAX_RETRIES ]; do
    # ابتدا سرور را بیدار می‌کنیم
    curl -s https://elen-backend-v2.onrender.com/api/health > /dev/null
    
    # سپس چک می‌کنیم که آیا مسیر ریاضی اضافه شده است یا خیر
    RESPONSE=$(curl -s https://elen-backend-v2.onrender.com/openapi.json | grep -o '"/api/math/discover"')
    
    if [ -n "$RESPONSE" ]; then
        SUCCESS=1
        break
    fi
    
    COUNT=$((COUNT+1))
    echo "⏳ تلاش $COUNT از $MAX_RETRIES: سرور هنوز آماده نیست، ۳۰ ثانیه دیگر تلاش می‌کنیم..."
    sleep 30
done

echo "=================================================="
if [ $SUCCESS -eq 1 ]; then
    echo "🎉 [پیروزی نهایی]: سرور Render با موفقیت آپدیت شد و موتورهای ریاضی فعال شدند!"
    echo "👉 حالا به سایت بروید و دکمه 'اجرای کشف' را تست کنید."
else
    echo "⚠️ [هشدار]: سرور آپدیت شد اما هنوز مسیرهای جدید را نشان نمی‌دهد."
    echo "👉 ممکن است بیلد در Render طول کشیده باشد. ۲ دقیقه دیگر دستور تست را بزنید."
fi
echo "=================================================="
