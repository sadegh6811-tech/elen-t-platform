import os
import time
import urllib.request
import json

HOOK_FILE = os.path.expanduser('~/.render_deploy_hook')
HOOK_URL = ""

print("==================================================")
print("🤖 [ربات جامع دیپلوی]: شروع عملیات خودکار...")
print("==================================================")

# ۱. بررسی وجود لینک در حافظه
if os.path.exists(HOOK_FILE):
    with open(HOOK_FILE, 'r') as f:
        HOOK_URL = f.read().strip()

# ۲. گرفتن لینک از کاربر در صورت نیاز
if not HOOK_URL.startswith("https://api.render.com/deploy/"):
    print("⚠️ لینک Deploy Hook در حافظه ربات یافت نشد.")
    print("👉 لطفاً به داشبورد Render بروید (Settings -> Deploy Hook)، یک لینک بسازید و کپی کنید.")
    while True:
        url = input("🔗 لینک Deploy Hook را اینجا پیست کنید و Enter بزنید: ").strip()
        if url.startswith("https://api.render.com/deploy/"):
            HOOK_URL = url
            with open(HOOK_FILE, 'w') as f:
                f.write(HOOK_URL)
            print("✅ لینک معتبر است و برای همیشه ذخیره شد.")
            break
        else:
            print("❌ خطا: لینک نامعتبر است. باید با https://api.render.com/deploy/ شروع شود. دوباره تلاش کنید.")

# ۳. ارسال دستور دیپلوی به Render
print("\n🚀 [مرحله ۱]: در حال ارسال دستور دیپلوی به Render...")
try:
    req = urllib.request.Request(HOOK_URL, method='POST')
    with urllib.request.urlopen(req) as response:
        if response.status in [200, 201]:
            print("✅ دستور دیپلوی با موفقیت ارسال شد. سرور در حال بیلد است...")
        else:
            print(f"❌ خطا: سرور Render درخواست را نپذیرفت (کد HTTP: {response.status}).")
            exit(1)
except Exception as e:
    print(f"❌ خطا در ارتباط با Render: {e}")
    exit(1)

# ۴. انتظار و تست خودکار (بدون نیاز به خروج از اسکریپت)
print("\n⏳ [مرحله ۲]: ربات به مدت ۶۰ ثانیه صبر می‌کند تا Render بیلد شود...")
time.sleep(60)

print("\n🧪 [مرحله ۳]: شروع تست خودکار سرور برای رویت موتور ریاضی (تا ۵ بار تلاش)...")
MAX_RETRIES = 5

for count in range(1, MAX_RETRIES + 1):
    print(f"   ⏳ تلاش {count} از {MAX_RETRIES}...")
    
    # بیدار کردن سرور (چون سرورهای رایگان می‌خوابند)
    try:
        urllib.request.urlopen("https://elen-backend-v2.onrender.com/api/health", timeout=15)
    except:
        pass
        
    # بررسی مسیر ریاضی
    try:
        with urllib.request.urlopen("https://elen-backend-v2.onrender.com/openapi.json", timeout=15) as resp:
            data = resp.read().decode('utf-8')
            if '"/api/math/discover"' in data:
                print("\n==================================================")
                print("🎉 [پیروزی نهایی]: سرور با موفقیت آپدیت شد و موتورهای ریاضی فعال شدند!")
                print("👉 حالا به سایت بروید، لاگین کنید و روی 'موتور محاسباتی' کلیک کنید.")
                print("==================================================")
                exit(0)
    except Exception:
        pass # در صورت خطا، در تلاش بعدی دوباره چک می‌کند

    if count < MAX_RETRIES:
        print("   ⏳ هنوز آماده نیست... ۳۰ ثانیه دیگر دوباره تلاش می‌کنم.")
        time.sleep(30)

print("\n==================================================")
print("⚠️ [هشدار]: بیلد در Render بیشتر از حد معمول طول کشیده است.")
print("👉 ممکن است سرور Render در حال روشن شدن باشد. لطفاً ۲ دقیقه دیگر دستور زیر را در ترمینال بزنید:")
print("curl -s https://elen-backend-v2.onrender.com/openapi.json | grep -o '\"/[^\"]*\"'")
print("==================================================")
