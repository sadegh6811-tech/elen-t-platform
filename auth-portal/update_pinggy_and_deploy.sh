#!/data/data/com.termux/files/usr/bin/bash
echo "🔗 لطفاً لینک جدید Pinggy را اینجا پیست کنید و Enter بزنید:"
read -r NEW_URL

if [ -z "$NEW_URL" ]; then
    echo "❌ لینک وارد نشد! عملیات لغو شد."
    exit 1
fi

cd ~/Nazi/auth-portal || { echo "❌ پوشه پیدا نشد"; exit 1; }

echo "🧹 حذف لینک قبلی..."
unset VERCEL_TOKEN
vercel env rm VITE_API_URL production --yes > /dev/null 2>&1

echo "🔗 ست کردن لینک جدید در ورسل..."
echo "$NEW_URL" | vercel env add VITE_API_URL production > /dev/null 2>&1

echo "🚀 دیپلوی نهایی با لینک جدید..."
vercel --prod --yes --force > deploy_final.log 2>&1

if grep -q "Ready in" deploy_final.log; then
    echo "🏆 پیروزی! سایت با لینک جدید آپدیت شد."
    grep -E "Production|Aliased" deploy_final.log
else
    echo "❌ خطا در دیپلوی. لاگ:"
    tail -n 15 deploy_final.log
fi
