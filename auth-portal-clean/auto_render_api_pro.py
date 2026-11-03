import os
import time
import urllib.request
import json

API_KEY_FILE = os.path.expanduser('~/.render_api_key')
SERVICE_ID = "srv-dbje2lgae00c73dv3a20"
API_KEY = ""

print("==================================================")
print("🤖 [ربات هوشمند API]: شروع فرآیند با کلید ورود...")
print("==================================================")

# ۱. دریافت API Key
if os.path.exists(API_KEY_FILE):
    with open(API_KEY_FILE, 'r') as f:
        API_KEY = f.read().strip()

if not API_KEY.startswith("rnd_"):
    print("⚠️ ربات به Render API Key نیاز دارد (همان کلیدی که در تصویر اول دیدید).")
    while True:
        key = input("🔑 لطفاً API Key (با rnd_...) را پیست کنید: ").strip()
        if key.startswith("rnd_"):
            API_KEY = key
            with open(API_KEY_FILE, 'w') as f:
                f.write(API_KEY)
            print("✅ API Key برای همیشه ذخیره شد.")
            break
        else:
            print("❌ خطا: API Key نامعتبر است.")

# ۲. ارسال دستور دیپلوی
print("\n🚀 [مرحله ۱]: ارسال دستور دیپلوی به Render...")
url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
data = json.dumps({"clearCache": "do_not_clear"}).encode('utf-8')

try:
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req) as response:
        resp_data = json.loads(response.read().decode('utf-8'))
        deploy_id = resp_data.get('id')
        print(f"✅ دیپلوی آغاز شد. (شناسه دیپلوی: {deploy_id})")
except Exception as e:
    print(f"❌ خطا در ارتباط با Render API: {e}")
    exit(1)

# ۳. رصد وضعیت بیلد از طریق API (هوشمندترین بخش)
print("\n⏳ [مرحله ۲]: ربات وضعیت بیلد در Render را رصد می‌کند (تا ۱۰ دقیقه)...")
print("این کار ممکن است چند دقیقه طول بکشد. لطفاً صبر کنید...")

check_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys/{deploy_id}"
MAX_RETRIES = 20 # 20 * 30s = 10 minutes

for count in range(1, MAX_RETRIES + 1):
    time.sleep(30) # هر ۳۰ ثانیه چک می‌کند
    print(f"   ⏳ بررسی وضعیت (تلاش {count})...", end=" ")
    
    try:
        req_check = urllib.request.Request(check_url, headers=headers, method='GET')
        with urllib.request.urlopen(req_check) as resp:
            status_data = json.loads(resp.read().decode('utf-8'))
            status = status_data.get('status')
            
            if status == 'live':
                print("✅ بیلد با موفقیت انجام شد و سرور Live است!")
                print("\n🧪 [مرحله ۳]: تست نهایی موتور ریاضی...")
                try:
                    with urllib.request.urlopen("https://elen-backend-v2.onrender.com/openapi.json", timeout=15) as api_resp:
                        api_data = api_resp.read().decode('utf-8')
                        if '"/api/math/discover"' in api_data:
                            print("\n==================================================")
                            print("🎉 [پیروزی نهایی]: موتورهای ریاضی فعال شدند!")
                            print("👉 حالا به سایت بروید و دکمه 'اجرای کشف' را تست کنید.")
                            print("==================================================")
                            exit(0)
                        else:
                            print("⚠️ سرور Live است اما مسیر ریاضی هنوز در openapi.json نیست.")
                            exit(1)
                except Exception as e:
                    print(f"⚠️ خطا در تست مسیر: {e}")
                    exit(1)
                    
            elif status == 'build_failed':
                print("❌ بیلد در Render با شکست مواجه شد!")
                print("👉 لطفاً لاگ‌های Render را بررسی کنید (مشکل معمولاً کمبود یک کتابخانه در requirements.txt است).")
                exit(1)
            else:
                print(f"⏳ در حال انجام... (وضعیت: {status})")
                
    except Exception as e:
        print(f"⚠️ خطا در بررسی وضعیت: {e}")

print("\n⚠️ زمان انتظار (۱۰ دقیقه) به پایان رسید.")
print("👉 لطفاً به داشبورد Render بروید و دستی وضعیت را بررسی کنید.")
