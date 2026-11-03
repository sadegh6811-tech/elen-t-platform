#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - V15 (API Protection Disabler)
# ==========================================================

PROJECT_DIR=~/Nazi/auth-portal
PROJECT_NAME="auth-portal"

cd $PROJECT_DIR || { echo "❌ پوشه پیدا نشد"; exit 1; }

# دریافت توکن جدید از کاربر
echo "🔑 لطفاً توکن جدید Vercel خود را وارد کنید (یا Enter بزنید تا از توکن قبلی استفاده شود):"
read -r NEW_TOKEN

if [ -n "$NEW_TOKEN" ]; then
    export VERCEL_TOKEN="$NEW_TOKEN"
    echo "✅ توکن جدید تنظیم شد."
else
    unset VERCEL_TOKEN
    echo "⚠️ از توکن یا نشست فعلی استفاده می‌شود."
fi

# ۱. تلاش برای خاموش کردن Deployment Protection از طریق API
if [ -n "$VERCEL_TOKEN" ]; then
    echo "🛡️ در حال خاموش کردن Deployment Protection (Vercel Authentication)..."
    
    # ارسال درخواست به API ورسل
    RESPONSE=$(curl -s -X PATCH "https://api.vercel.com/v9/projects/$PROJECT_NAME" \
        -H "Authorization: Bearer $VERCEL_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"ssoProtection": null, "passwordProtection": null}')

    if echo "$RESPONSE" | grep -q '"id"'; then
        echo "🏆 موفق! محافظ ورسل (Deployment Protection) با موفقیت خاموش شد."
    else
        echo "⚠️ ربات نتوانست محافظ را خاموش کند. (احتمالا توکن دسترسی کافی ندارد)."
        echo "لطفاً این کار را به صورت دستی در داشبورد Vercel انجام دهید."
    fi
else
    echo "⚠️ توکنی برای ارتباط با API ورسل وجود ندارد."
    echo "لطفاً Deployment Protection را به صورت دستی در داشبورد Vercel خاموش کنید."
fi

# ۲. دیپلوی نهایی
echo "🚀 در حال ارسال نهایی به Vercel..."
vercel --prod --yes --force > deploy_final.log 2>&1

if grep -q "Ready in" deploy_final.log; then
    echo "🎉 دیپلوی با موفقیت انجام شد."
    grep -E "Production|Aliased" deploy_final.log
else
    echo "❌ خطا در دیپلوی."
fi
