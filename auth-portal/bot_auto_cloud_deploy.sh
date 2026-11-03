#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - Full Auto-Cloud Deployment Module
# ==========================================================

echo "☁️ ربات: آغاز فرآیند انتقال نهایی به سرور ابری (Render)"
echo "----------------------------------------------------------"

cd ~/سبزی || { echo "❌ پوشه سبزی پیدا نشد"; exit 1; }

# ۱. دریافت اطلاعات گیت‌هاب
echo "🔗 لطفاً لینک ریپازیتوری گیت‌هاب خود را وارد کنید (مثال: https://github.com/username/repo.git):"
read -r GITHUB_URL

echo "🔑 لطفاً Personal Access Token گیت‌هاب خود را وارد کنید (برای احراز هویت):"
read -r GITHUB_TOKEN

if [ -z "$GITHUB_URL" ] || [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ لینک یا توکن وارد نشد! عملیات لغو شد."
    exit 1
fi

echo "⚙️ ربات در حال آماده‌سازی و ارسال کدها به گیت‌هاب..."

# استخراج لینک با احراز هویت
AUTH_URL=$(echo "$GITHUB_URL" | sed "s/https:\/\//https:\/\/$GITHUB_TOKEN@/")

# پاکسازی ریموت قبلی (اگر وجود داشته باشد)
git remote remove origin 2>/dev/null || true

# افزودن ریموت جدید و پوش کردن کدها
git remote add origin "$AUTH_URL"
git branch -M main
git push -u origin main > push_log.txt 2>&1

if grep -q "main -> main" push_log.txt || [ $? -eq 0 ]; then
    echo "🏆 پیروزی! کدهای بک‌اند با موفقیت به گیت‌هاب ارسال شدند."
    echo "----------------------------------------------------------"
    echo "🎯 آخرین مأموریت برای شما (فقط ۳۰ ثانیه):"
    echo "۱. به سایت render.com بروید و لاگین کنید."
    echo "۲. روی New + کلیک کرده و Web Service را انتخاب کنید."
    echo "۳. ریپازیتوری گیت‌هاب خود را انتخاب کنید."
    echo "۴. Render به صورت خودکار فایل render.yaml ما را می‌خواند."
    echo "۵. دکمه Create Web Service را بزنید."
    echo "----------------------------------------------------------"
    echo "💡 وقتی Render کارش را تمام کرد، یک لینک (مثل https://...onrender.com) به شما می‌دهد."
    echo "آن لینک را کپی کنید و به من بگویید تا با ربات آن را روی Vercel ست کنیم."
else
    echo "❌ خطا در ارسال به گیت‌هاب. لاگ خطا:"
    cat push_log.txt
fi
