#!/bin/bash

echo "=================================================="
echo "🤖 [ربات دیپلوی Render]: شروع فرآیند آپدیت (قدم ۱)..."
echo "=================================================="

HOOK_FILE="$HOME/.render_deploy_hook"
IS_VALID=0

# بررسی اینکه آیا لینک قبلی وجود دارد و معتبر است یا نه
if [ -f "$HOOK_FILE" ]; then
    EXISTING_HOOK=$(cat "$HOOK_FILE")
    if [[ "$EXISTING_HOOK" == https://api.render.com/deploy/* ]]; then
        IS_VALID=1
        echo "✅ لینک Deploy Hook از قبل ذخیره شده و معتبر است."
    fi
fi

# اگر لینک معتبر نبود، از کاربر بگیرد و اعتبارسنجی کند
if [ $IS_VALID -eq 0 ]; then
    echo "⚠️ لینک معتبری یافت نشد."
    while true; do
        read -p "🔗 لطفاً لینک Deploy Hook را (که با https://api.render.com/deploy/ شروع می‌شود) پیست کنید: " INPUT_URL
        if [[ "$INPUT_URL" == https://api.render.com/deploy/* ]]; then
            echo -n "$INPUT_URL" > "$HOOK_FILE"
            HOOK_URL="$INPUT_URL"
            echo "✅ لینک معتبر است و ذخیره شد."
            break
        else
            echo "❌ خطا: لینک نامعتبر است! باید با https://api.render.com/deploy/ شروع شود. دوباره تلاش کنید."
        fi
    done
else
    HOOK_URL=$(cat "$HOOK_FILE")
fi

# ارسال دستور دیپلوی به Render
echo "🚀 در حال ارسال دستور دیپلوی به Render..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$HOOK_URL")

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
    echo "✅ دستور دیپلوی با موفقیت ارسال شد. سرور در حال ساخت (Build) است..."
else
    echo "❌ خطا: سرور Render درخواست را نپذیرفت (کد HTTP: $HTTP_CODE)."
    echo "لطفاً مطمئن شوید لینک را از بخش Settings -> Deploy Hook درست کپی کرده‌اید."
    exit 1
fi

# انتظار و بررسی خودکار
echo "⏳ [مرحله ۲]: صبر برای بیلد شدن در Render (حدود ۹۰ ثانیه)..."
sleep 60

MAX_RETRIES=4
COUNT=1

while [ $COUNT -le $MAX_RETRIES ]; do
    echo "🧪 تست نهایی (تلاش $COUNT از $MAX_RETRIES)..."
    
    # بیدار کردن سرور
    curl -s https://elen-backend-v2.onrender.com/api/health > /dev/null
    
    # بررسی مسیر ریاضی
    RESPONSE=$(curl -s https://elen-backend-v2.onrender.com/openapi.json | grep -o '"/api/math/discover"')
    
    if [ -n "$RESPONSE" ]; then
        echo "=================================================="
        echo "🎉 [پیروزی نهایی]: سرور با موفقیت آپدیت شد و موتورهای ریاضی فعال شدند!"
        echo "👉 حالا به سایت بروید و روی 'موتور محاسباتی' کلیک کنید."
        echo "=================================================="
        exit 0
    fi
    
    COUNT=$((COUNT+1))
    if [ $COUNT -le $MAX_RETRIES ]; then
        echo "⏳ هنوز آماده نیست... ۳۰ ثانیه دیگر دوباره تلاش می‌کنیم."
        sleep 30
    fi
done

echo "=================================================="
echo "⚠️ [هشدار]: بیلد در Render بیشتر از حد معمول طول کشیده است."
echo "👉 لطفاً ۲ دقیقه دیگر صبر کنید و دستور تست را دستی بزنید:"
echo "curl -s https://elen-backend-v2.onrender.com/openapi.json | grep -o '\"/[^\"]*\"'"
echo "=================================================="
