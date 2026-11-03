#!/bin/bash

echo "🤖 [ربات]: شروع عملیات نهایی و رفع خطای دیتابیس..."

# ==========================================
# تنظیمات نهایی (لینک با رمز صحیح شما)
# ==========================================
MONGO_URI="mongodb+srv://elena_admin:Karami16068@cluster0.9x2849b.mongodb.net/?retryWrites=true&w=majority"
JWT_SECRET="Elen_Super_Secret_Key_2026_Secure_Token_!!"
TOKEN=$(cat ~/.vercel-token)

# ۱. پاک کردن لینک‌های قبلی برای جلوگیری از تداخل
echo "🗑️ [مرحله ۱]: پاک کردن تنظیمات قدیمی..."
echo "y" | npx vercel env rm MONGODB_URI production --token $TOKEN > /dev/null 2>&1
echo "y" | npx vercel env rm JWT_SECRET production --token $TOKEN > /dev/null 2>&1
echo "✅ پاکسازی انجام شد."

# ۲. ذخیره لینک جدید با printf (بدون کاراکتر اضافه)
echo "➕ [مرحله ۲]: ذخیره لینک دیتابیس..."
printf "%s" "$MONGO_URI" | npx vercel env add MONGODB_URI production --token $TOKEN
echo "✅ لینک دیتابیس ذخیره شد."

# ۳. ذخیره کلید امنیتی
echo "🔐 [مرحله ۳]: ذخیره کلید امنیتی..."
printf "%s" "$JWT_SECRET" | npx vercel env add JWT_SECRET production --token $TOKEN
echo "✅ کلید امنیتی ذخیره شد."

# ۴. آپلود نهایی روی Vercel
echo "🚀 [مرحله ۴]: در حال آپلود روی Vercel (لطفا صبر کنید)..."
npx vercel --prod --yes --token $TOKEN

echo "=================================================="
echo "🎉 [ربات]: عملیات تمام شد! حالا تست نهایی را بزنید."
echo "=================================================="
