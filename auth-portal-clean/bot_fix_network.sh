#!/bin/bash

echo "🤖 [ربات عیب‌یاب]: شروع بررسی و رفع خطای Network Error..."

# ==========================================
# ۱. اصلاح فایل فرانت‌اند (AuthCard.tsx)
# ==========================================
echo "🔍 [مرحله ۱]: بررسی آدرس API در فرانت‌اند..."
python3 -c "
import re
path = 'src/components/AuthCard.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# اگر آدرس اشتباهی وجود دارد، آن را به مسیر نسبی درست تغییر بده
if 'YOUR_REAL_BACKEND_URL' in content or 'http://localhost' in content:
    content = re.sub(r'const API_URL = .*;', '', content)
    content = content.replace('fetch(API_URL + ', 'fetch(')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ آدرس‌های اشتباه در AuthCard.tsx اصلاح شدند.')
else:
    print('✅ AuthCard.tsx از قبل درست است.')
"

# ==========================================
# ۲. تزریق هدرهای CORS در بک‌اند (در صورت نبود)
# ==========================================
echo "🔍 [مرحله ۲]: بررسی هدرهای CORS در فایل‌های API..."
cat > fix_cors.py << 'PYEOF'
import os

def fix_cors(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    cors_code = """
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();
"""
    # اگر هدرها وجود نداشتند، آن‌ها را بعد از شروع تابع handler اضافه کن
    if 'Access-Control-Allow-Origin' not in content:
        # پیدا کردن خط شروع تابع handler
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'export default async function handler' in line:
                lines.insert(i + 2, cors_code) # بعد از خط { تابع
                break
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f'✅ هدرهای CORS به {filepath} اضافه شدند.')
    else:
        print(f'✅ هدرهای CORS در {filepath} از قبل وجود دارند.')

fix_cors('api/register.js')
fix_cors('api/login.js')
PYEOF
python3 fix_cors.py && rm fix_cors.py

# ==========================================
# ۳. بیلد و دیپلوی مجدد
# ==========================================
echo "🚀 [مرحله ۳]: آپلود نسخه اصلاح‌شده روی Vercel..."
npx vercel --prod --yes --token $(cat ~/.vercel-token)

echo "=================================================="
echo "🎉 [ربات]: عملیات عیب‌یابی و تعمیر تمام شد!"
echo "⚠️ [نکته مهم]: حتماً سایت را در مرورگر با (Ctrl+F5) یا در تب ناشناس باز کنید."
echo "=================================================="
