import os
import time
import urllib.request

HOOK_FILE = os.path.expanduser('~/.render_deploy_hook')
HOOK_URL = ""

# ۱. بررسی لینک ذخیره شده
if os.path.exists(HOOK_FILE):
    with open(HOOK_FILE, 'r') as f:
        HOOK_URL = f.read().strip()

# ۲. اگر لینک معتبر نبود، از کاربر بگیرد
if not HOOK_URL.startswith("https://api.render.com/deploy/"):
    print("==================================================")
    print("⚠️ لینک Deploy Hook یافت نشد یا نامعتبر است.")
    print("لطفاً به داشبورد Render بروید (Settings -> Deploy Hook) و لینک را کپی کنید.")
    print("==================================================")
    while True:
        url = input("🔗 لینک Deploy Hook را اینجا پیست کنید: ").strip()
        if url.startswith("https://api.render.com/deploy/"):
            HOOK_URL = url
            with open(HOOK_FILE, 'w') as f:
                f.write(HOOK_URL)
            print("✅ لینک معتبر است و ذخیره شد.")
            break
        else:
            print("❌ خطا: لینک نامعتبر است! باید با https://api.render.com/deploy/ شروع شود. دوباره تلاش کنید.")

# ۳. ارسال دستور دیپلوی به Render
print("\n🚀 در حال ارسال دستور دیپلوی به Render...")
try:
    req = urllib.request.Request(HOOK_URL, method='POST')
    with urllib.request.urlopen(req) as response:
        if response.status in [200, 201]:
            print("✅ دستور دیپلوی با موفقیت ارسال شد. سرور در حال ساخت (Build) است...")
        else:
            print(f"❌ خطا: سرور Render درخواست را نپذیرفت (کد HTTP: {response.status}).")
            exit(1)
except Exception as e:
    print(f"❌ خطا در ارتباط با Render: {e}")
    exit(1)

# ۴. انتظار و تست خودکار
print("\n⏳ صبر برای بیلد شدن در Render (حدود ۹۰ ثانیه)...")
time.sleep(60)

MAX_RETRIES = 4
for count in range(1, MAX_RETRIES + 1):
    print(f"🧪 تست نهایی (تلاش {count} از {MAX_RETRIES})...")
    
    # بیدار کردن سرور
    try:
        urllib.request.urlopen("https://elen-backend-v2.onrender.com/api/health", timeout=10)
    except:
        pass
        
    # بررسی مسیر ریاضی
    try:
        with urllib.request.urlopen("https://elen-backend-v2.onrender.com/openapi.json", timeout=10) as resp:
            data = resp.read().decode('utf-8')
            if '"/api/math/discover"' in data:
                print("\n==================================================")
                print("🎉 [پیروزی نهایی]: سرور با موفقیت آپدیت شد و موتورهای ریاضی فعال شدند!")
                print("👉 حالا به سایت بروید، لاگین کنید و روی 'موتور محاسباتی' کلیک کنید.")
                print("==================================================")
                exit(0)
    except Exception as e:
        pass # در صورت خطای شبکه، در تلاش بعدی دوباره تست می‌کند

    if count < MAX_RETRIES:
        print("⏳ هنوز آماده نیست... ۳۰ ثانیه دیگر دوباره تلاش می‌کنیم.")
        time.sleep(30)

print("\n==================================================")
print("⚠️ [هشدار]: بیلد در Render بیشتر از حد معمول طول کشیده است.")
print("👉 لطفاً ۲ دقیقه دیگر صبر کنید و دستی در سایت تست کنید.")
print("==================================================")
