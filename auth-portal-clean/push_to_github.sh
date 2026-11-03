#!/data/data/com.termux/files/usr/bin/bash
echo "🔗 لطفاً لینک مخزن گیت‌هاب خود را که کپی کردید، اینجا پیست کنید (مثال: https://github.com/sadegh6811/elen-t-pla.git):"
read -r REPO_URL

echo "🔑 لطفاً توکن گیت‌هاب خود (که با ghp_ شروع می‌شود) را پیست کنید:"
read -r TOKEN

if [ -z "$REPO_URL" ] || [ -z "$TOKEN" ]; then
    echo "❌ لینک یا توکن خالی است! عملیات لغو شد."
    exit 1
fi

# ذخیره توکن برای دفعات بعدی
echo "$TOKEN" > ~/.github_token

cd ~/سبزی || { echo "❌ پوشه سبزی پیدا نشد"; exit 1; }

echo "🚀 در حال ارسال کدها به گیت‌هاب..."

# پاک کردن ریموت قبلی و اضافه کردن ریموت جدید با توکن
git remote remove origin 2>/dev/null || true
# حذف https:// از ابتدای لینک برای تزریق توکن
CLEAN_URL=$(echo "$REPO_URL" | sed 's|https://||')
git remote add origin "https://$TOKEN@$CLEAN_URL"

git branch -M main
git add requirements.txt render.yaml public_proxy.py security_sensor.py security_engine.py .gitignore
git commit -m "ELEN Backend ready for Render" > /dev/null 2>&1

git push -u origin main -f

if [ $? -eq 0 ]; then
    echo "🏆 پیروزی! کدها با موفقیت روی گیت‌هاب آپلود شدند."
    echo "=========================================================="
    echo "🎯 مأموریت شما:"
    echo "به سایت render.com بروید، روی New Web Service کلیک کنید، مخزن را انتخاب کنید و Deploy را بزنید."
else
    echo "❌ خطا در آپلود به گیت‌هاب. لطفاً مطمئن شوید توکن شما دسترسی repo دارد."
fi
