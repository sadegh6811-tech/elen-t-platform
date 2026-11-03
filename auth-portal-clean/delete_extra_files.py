import os
import json
import urllib.request
import time

# --- تنظیمات ---
GITHUB_TOKEN_FILE = os.path.expanduser('~/.github_token')
RENDER_API_KEY_FILE = os.path.expanduser('~/.render_api_key')
REPO = "sadegh6811-tech/devstudio-bot"
SERVICE_ID = "srv-dbje2lgae00c73dv3a20"

print("==================================================")
print("🤖 [ربات پاکسازی]: شروع عملیات حذف فایل‌های اضافه...")
print("==================================================")

# خواندن توکن‌ها
try:
    with open(GITHUB_TOKEN_FILE, 'r') as f: gh_token = f.read().strip()
    with open(RENDER_API_KEY_FILE, 'r') as f: render_key = f.read().strip()
except Exception as e:
    print("❌ خطا در خواندن توکن‌ها. مطمئن شوید هر دو توکن ذخیره شده‌اند.")
    exit(1)

# --- مرحله ۱: حذف فایل‌های اضافه از گیت‌هاب ---
print("\n🗑️ [مرحله ۱]: در حال حذف فایل‌های اضافه از گیت‌هاب...")
files_to_delete = ['main.py', 'app.py', 'auth_portal.py']
for file in files_to_delete:
    url = f"https://api.github.com/repos/{REPO}/contents/{file}"
    headers = {'Authorization': f'token {gh_token}', 'Accept': 'application/vnd.github.v3+json'}
    
    try:
        # دریافت SHA فایل (برای حذف نیاز است)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            sha = json.loads(resp.read().decode())['sha']
            
        # ارسال درخواست حذف
        data = json.dumps({'message': f'chore: delete {file}', 'sha': sha}).encode('utf-8')
        req_del = urllib.request.Request(url, data=data, headers=headers, method='DELETE')
        urllib.request.urlopen(req_del)
        print(f"✅ فایل {file} با موفقیت حذف شد.")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"ℹ️ فایل {file} از قبل وجود نداشت.")
        else:
            print(f"❌ خطا در حذف {file}: {e}")
    except Exception as e:
        print(f"❌ خطای غیرمنتظره در حذف {file}: {e}")

# --- مرحله ۲: دیپلوی مجدد در Render ---
print("\n🚀 [مرحله ۲]: در حال ارسال دستور دیپلوی به Render...")
render_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
render_headers = {
    "Authorization": f"Bearer {render_key}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
render_data = json.dumps({"clearCache": "do_not_clear"}).encode('utf-8')

try:
    req_deploy = urllib.request.Request(render_url, data=render_data, headers=render_headers, method='POST')
    with urllib.request.urlopen(req_deploy) as resp:
        deploy_data = json.loads(resp.read().decode())
        deploy_id = deploy_data.get('id')
        print(f"✅ دیپلوی آغاز شد. (شناسه: {deploy_id})")
except Exception as e:
    print(f"❌ خطا در ارتباط با Render API: {e}")
    exit(1)

# --- مرحله ۳: رصد وضعیت و تست نهایی ---
print("\n⏳ [مرحله ۳]: ربات وضعیت بیلد را رصد می‌کند (لطفا صبر کنید)...")
check_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys/{deploy_id}"

for count in range(1, 21): # تا ۱۰ دقیقه
    time.sleep(30)
    print(f"   ⏳ بررسی وضعیت (تلاش {count})...", end=" ")
    
    try:
        req_check = urllib.request.Request(check_url, headers=render_headers, method='GET')
        with urllib.request.urlopen(req_check) as resp:
            status_data = json.loads(resp.read().decode())
            status = status_data.get('status')
            
            if status == 'live':
                print("✅ بیلد با موفقیت انجام شد و سرور Live است!")
                print("\n🧪 [مرحله ۴]: تست نهایی موتور ریاضی...")
                try:
                    with urllib.request.urlopen("https://elen-backend-v2.onrender.com/openapi.json", timeout=15) as api_resp:
                        api_data = api_resp.read().decode('utf-8')
                        if '"/api/math/discover"' in api_data:
                            print("\n==================================================")
                            print("🎉 [پیروزی نهایی]: فایل‌های اضافه پاک شدند و موتورهای ریاضی فعال شدند!")
                            print("👉 حالا به سایت بروید و دکمه 'اجرای کشف' را تست کنید.")
                            print("==================================================")
                            exit(0)
                        else:
                            print("⚠️ سرور Live است اما مسیر ریاضی هنوز در openapi.json نیست.")
                            print("👉 ممکن است فایل دیگری در گیت‌هاب باشد. لطفا لاگ‌های Render را چک کنید.")
                            exit(1)
                except Exception as e:
                    print(f"⚠️ خطا در تست مسیر: {e}")
                    exit(1)
            elif status == 'build_failed':
                print("❌ بیلد در Render با شکست مواجه شد!")
                exit(1)
            else:
                print(f"⏳ در حال انجام... (وضعیت: {status})")
    except Exception as e:
        print(f"⚠️ خطا در بررسی وضعیت: {e}")

print("\n⚠️ زمان به پایان رسید. لطفاً داشبورد Render را دستی بررسی کنید.")
