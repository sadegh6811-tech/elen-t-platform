#!/bin/bash

echo "🤖 [ربات دیپلوی]: شروع عملیات خودکار..."

# ==========================================
# ۱. تنظیمات (لینک و رمز شما)
# ==========================================
MONGO_URI="mongodb+srv://elena_admin:elen1234@cluster0.9x2849b.mongodb.net/?retryWrites=true&w=majority"
JWT_SECRET="Elen_Super_Secret_Key_2026_Secure_Token_!!"
TOKEN=$(cat ~/.vercel-token)

# ==========================================
# ۲. پاک کردن تنظیمات قدیمی (برای جلوگیری از تداخل)
# ==========================================
echo "🗑️ [مرحله ۱]: پاک کردن متغیرهای قدیمی..."
echo "y" | npx vercel env rm MONGODB_URI production --token $TOKEN > /dev/null 2>&1
echo "y" | npx vercel env rm JWT_SECRET production --token $TOKEN > /dev/null 2>&1
echo "✅ پاکسازی انجام شد."

# ==========================================
# ۳. اضافه کردن دیتابیس با printf (بدون کاراکتر اضافه)
# ==========================================
echo "➕ [مرحله ۲]: ذخیره لینک دیتابیس..."
printf "%s" "$MONGO_URI" | npx vercel env add MONGODB_URI production --token $TOKEN
echo "✅ لینک دیتابیس ذخیره شد."

# ==========================================
# ۴. اضافه کردن کلید امنیتی
# ==========================================
echo "🔐 [مرحله ۳]: ذخیره کلید امنیتی JWT..."
printf "%s" "$JWT_SECRET" | npx vercel env add JWT_SECRET production --token $TOKEN
echo "✅ کلید امنیتی ذخیره شد."

# ==========================================
# ۵. آپلود نهایی روی Vercel
# ==========================================
echo "🚀 [مرحله ۴]: در حال آپلود روی Vercel (لطفا صبر کنید)..."
npx vercel --prod --yes --token $TOKEN

echo "=================================================="
echo "🎉 [ربات دیپلوی]: تمام کارها با موفقیت انجام شد!"
echo "=================================================="
