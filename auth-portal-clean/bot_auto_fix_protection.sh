#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - V16 (Autonomous Token Extractor)
# ==========================================================

echo "🕵️‍♂️ ربات در حال جستجو برای پیدا کردن کلید دیجیتال (Token) در گوشی شماست..."

# مسیرهای احتمالی ذخیره توکن توسط Vercel CLI در Termux
TOKEN_PATHS=(
    "$HOME/.local/share/com.vercel.cli/auth.json"
    "$HOME/.vercel/auth.json"
    "$HOME/.config/vercel/auth.json"
)

V_TOKEN=""

# جستجو در مسیرهای مختلف
for path in "${TOKEN_PATHS[@]}"; do
    if [ -f "$path" ]; then
        # استخراج توکن از فایل JSON
        V_TOKEN=$(python -c "import json; print(json.load(open('$path')).get('token', ''))" 2>/dev/null)
        if [ -n "$V_TOKEN" ]; then
            echo "✅ کلید دیجیتال با موفقیت در مسیر $path پیدا شد."
            break
        fi
    fi
done

# اگر ربات توکن را پیدا نکرد
if [ -z "$V_TOKEN" ]; then
    echo "❌ ربات نتوانست توکن را به صورت خودکار پیدا کند."
    echo "💡 لطفاً یک بار دستور 'vercel login' را در ترمینال بزنید و دوباره تلاش کنید."
    exit 1
fi

echo "🛡️ در حال ارسال درخواست به Vercel برای خاموش کردن محافظ (Deployment Protection)..."
echo "⏳ لطفاً چند لحظه صبر کنید..."

# ارسال درخواست PATCH به API ورسل برای غیرفعال کردن محافظ
RESPONSE=$(curl -s -X PATCH "https://api.vercel.com/v9/projects/auth-portal" \
    -H "Authorization: Bearer $V_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"ssoProtection": null, "passwordProtection": null}')

# بررسی نتیجه
if echo "$RESPONSE" | grep -q '"id"'; then
    echo "🏆 پیروزی! ربات محافظ ورسل را با موفقیت خاموش کرد."
    echo "✅ سایت شما الان برای همه قابل دسترسی است."
else
    echo "⚠️ ربات نتوانست محافظ را خاموش کند. پاسخ ورسل:"
    echo "$RESPONSE"
    echo "💡 این احتمال وجود دارد که پلن رایگان ورسل اجازه این کار را از طریق API ندهد."
    echo "لطفاً یک بار به صورت دستی به داشبورد Vercel بروید و Deployment Protection را Disabled کنید."
fi
