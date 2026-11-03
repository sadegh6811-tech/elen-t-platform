import os
import time
import urllib.request
import json
import ssl

API_KEY_FILE = os.path.expanduser('~/.render_api_key')
SERVICE_ID = "srv-dbje2lgae00c73dv3a20"
API_KEY = ""

print("==================================================")
print("🤖 [ربات جامع]: شروع عملیات خودکار (تغییر Start Command + دیپلوی + تست)...")
print("==================================================")

# ۱. خواندن API Key
try:
    with open(API_KEY_FILE, 'r') as f:
        API_KEY = f.read().strip()
    if not API_KEY.startswith("rnd_"):
        raise ValueError("Invalid Key")
except Exception:
    print("⚠️ API Key یافت نشد یا نامعتبر است.")
    API_KEY = input("🔑 لطفاً API Key را پیست کنید: ").strip()
    with open(API_KEY_FILE, 'w') as f:
        f.write(API_KEY)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# ۲. تغییر Start Command در Render
print("\n🛠️ [مرحله ۱]: در حال تغییر Start Command در سرور Render...")
update_url = f"https://api.render.com/v1/services/{SERVICE_ID}"
update_data = {
    "serviceDetails": {
        "envSpecificDetails": {
            "startCommand": "uvicorn public_proxy:app --host 0.0.0.0 --port $PORT"
        }
    }
}

try:
    req = urllib.request.Request(update_url, data=json.dumps(update_data).encode('utf-8'), headers=headers, method='PATCH')
    with urllib.request.urlopen(req) as resp:
        print("✅ دستور اجرا (Start Command) با موفقیت به public_proxy تغییر یافت.")
except Exception as e:
    print(f"⚠️ خطا در تغییر Start Command: {e}")
    print("👉 ممکن است Render API ساختار متفاوتی داشته باشد، اما به تلاش ادامه می‌دهیم...")

# ۳. ارسال دستور دیپلوی جدید
print("\n🚀 [مرحله ۲]: ارسال دستور دیپلوی جدید به Render...")
deploy_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
deploy_data = json.dumps({"clearCache": "clear"}).encode('utf-8') # پاک کردن کش برای اعمال قطعی تغییرات

try:
    req_deploy = urllib.request.Request(deploy_url, data=deploy_data, headers=headers, method='POST')
    with urllib.request.urlopen(req_deploy) as resp:
        deploy_id = json.loads(resp.read().decode('utf-8')).get('id')
        print(f"✅ دیپلوی آغاز شد. (شناسه: {deploy_id})")
except Exception as e:
    print(f"❌ خطا در شروع دیپلوی: {e}")
    exit(1)

# ۴. رصد وضعیت بیلد
print("\n⏳ [مرحله ۳]: ربات وضعیت بیلد را رصد می‌کند (لطفا صبر کنید، این کار ۳ تا ۵ دقیقه طول می‌کشد)...")
check_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys/{deploy_id}"

for count in range(1, 21): # تا ۱۰ دقیقه
    time.sleep(30)
    print(f"   ⏳ بررسی وضعیت (تلاش {count})...", end=" ")
    
    try:
        req_check = urllib.request.Request(check_url, headers=headers, method='GET')
        with urllib.request.urlopen(req_check) as resp:
            status = json.loads(resp.read().decode('utf-8')).get('status')
            
            if status == 'live':
                print("✅ بیلد با موفقیت انجام شد و سرور Live است!")
                break
            elif status == 'build_failed':
                print("❌ بیلد در Render با شکست مواجه شد!")
                print("👉 لطفاً لاگ‌های Render را بررسی کنید.")
                exit(1)
            else:
                print(f"⏳ در حال انجام... (وضعیت: {status})")
    except Exception as e:
        print(f"⚠️ خطا در بررسی وضعیت (شبکه): {e}")

# ۵. تست نهایی
print("\n🧪 [مرحله ۴]: تست نهایی موتور ریاضی...")
time.sleep(5) # کمی صبر برای بالا آمدن کامل سرور
try:
    with urllib.request.urlopen("https://elen-backend-v2.onrender.com/openapi.json", timeout=15) as api_resp:
        api_data = api_resp.read().decode('utf-8')
        if '"/api/math/discover"' in api_data:
            print("\n==================================================")
            print("🎉 [پیروزی نهایی]: همه چیز خودکار انجام شد!")
            print("👉 موتورهای ریاضی روی سرور فعال شدند.")
            print("👉 حالا به سایت بروید و دکمه 'اجرای کشف' را تست کنید.")
            print("==================================================")
        else:
            print("\n⚠️ سرور Live است اما مسیر ریاضی هنوز پیدا نشد.")
            print("👉 متن Start Command را در Render چک کنید.")
except Exception as e:
    print(f"\n⚠️ خطا در تست نهایی: {e}")
