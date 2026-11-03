#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - Vercel Protection Disabler via API
# ==========================================================

echo "🛡️ ابزار خودکار خاموش کردن محافظ ورسل (Deployment Protection)"
echo "-------------------------------------------------------------"
echo "ربات به یک توکن (Token) معتبر از داشبورد ورسل نیاز دارد."
read -p "🔑 لطفاً توکن Vercel خود را اینجا پیست کنید و Enter بزنید: " V_TOKEN

if [ -z "$V_TOKEN" ]; then
    echo "❌ شما هیچ توکنی وارد نکردید! عملیات لغو شد."
    exit 1
fi

echo "⏳ در حال ارسال درخواست به Vercel API..."

# ارسال درخواست PATCH به API ورسل برای غیرفعال کردن محافظ
RESPONSE=$(curl -s -X PATCH "https://api.vercel.com/v9/projects/auth-portal" \
    -H "Authorization: Bearer $V_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"ssoProtection": null, "passwordProtection": null}')

# بررسی نتیجه
if echo "$RESPONSE" | grep -q '"id"'; then
    echo "🏆 موفق! محافظ Vercel (Deployment Protection) با موفقیت خاموش شد."
    echo "✅ سایت شما الان برای همه قابل دسترسی است."
else
    echo "❌ خطا در ارتباط با Vercel. پاسخ دریافتی:"
    echo "$RESPONSE"
    echo "⚠️ لطفاً مطمئن شوید توکن شما معتبر است."
fi
