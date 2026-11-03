import re

file_path = 'src/components/Karami.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. حذف کدهای خراب با استفاده از Regex (فرقی نمی‌کند چقدر فاصله داشته باشند)
# الگوی ...( || {} ) را پیدا می‌کند
content = re.sub(r'\.\.\.\(\s*\|\|\s*\{\}\s*\)', '', content)
content = re.sub(r'\.\.\.\(\s*\?\.headers\s*\|\|\s*\{\}\s*\)', '', content)

# 2. پاک کردن کاراکترهای اضافی در صورت وجود
content = content.replace('...( || {} ),', '')
content = content.replace('...( ?.headers || {} ),', '')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ فایل Karami.tsx با موفقیت اصلاح شد.")
