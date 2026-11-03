import os
import time
import urllib.request
import json
import subprocess

API_KEY_FILE = os.path.expanduser('~/.render_api_key')
GITHUB_TOKEN_FILE = os.path.expanduser('~/.github_token')
SERVICE_ID = "srv-dbje2lgae00c73dv3a20"
REPO = "sadegh6811-tech/devstudio-bot"

print("==================================================")
print("🤖 [ربات هوشمند]: شروع عملیات تعمیر و دیپلوی...")
print("==================================================")

# ۱. آپدیت فایل requirements.txt در گیت‌هاب
print("\n📦 [مرحله ۱]: آپدیت کتابخانه‌های مورد نیاز در گیت‌هاب...")
requirements = """fastapi
uvicorn
pandas
numpy
scikit-learn
python-multipart
requests
pydantic
"""
with open('requirements.txt', 'w') as f:
    f.write(requirements)

try:
    token = open(GITHUB_TOKEN_FILE, 'r').read().strip()
    path = 'requirements.txt'
    content = open('requirements.txt', 'rb').read()
    import base64
    b64 = base64.b64encode(content).decode('utf-8')
    
    req_get = urllib.request.Request(f'https://api.github.com/repos/{REPO}/contents/{path}', headers={'Authorization': f'token {token}'})
    try: sha = json.loads(urllib.request.urlopen(req_get).read().decode())['sha']
    except: sha = None
    
    data = {'message': 'fix: update requirements for public_proxy', 'content': b64}
    if sha: data['sha'] = sha
    
    req_put = urllib.request.Request(f'https://api.github.com/repos/{REPO}/contents/{path}', data=json.dumps(data).encode('utf-8'), headers={'Authorization': f'token {token}', 'Content-Type': 'application/json'}, method='PUT')
    urllib.request.urlopen(req_put)
    print("✅ فایل requirements.txt با موفقیت در گیت‌هاب آپدیت شد.")
except Exception as e:
    print(f"⚠️ خطا در آپدیت گیت‌هاب: {e}")

# ۲. ارسال دستور دیپلوی به Render
print("\n🚀 [مرحله ۲]: ارسال دستور دیپلوی به Render (با پاک کردن کش)...")
try:
    api_key = open(API_KEY_FILE, 'r').read().strip()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    deploy_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
    deploy_data = json.dumps({"clearCache": "clear"}).encode('utf-8')
    
    req = urllib.request.Request(deploy_url, data=deploy_data, headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        deploy_id = json.loads(resp.read().decode('utf-8')).get('id')
        print(f"✅ دیپلوی آغاز شد. (شناسه: {deploy_id})")
except Exception as e:
    print(f"❌ خطا در شروع دیپلوی: {e}")
    exit(1)

# ۳. رصد وضعیت بیلد
print("\n⏳ [مرحله ۳]: ربات وضعیت بیلد را رصد می‌کند (لطفا صبر کنید)...")
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
                print("❌ بیلد در Render شکست خورد!")
                print("👉 لطفاً عکس لاگ‌های Render را برای من بفرستید.")
                exit(1)
            else:
                print(f"⏳ ({status})")
    except Exception as e:
        print(f"⚠️ خطای شبکه: {e}")

# ۴. تست نهایی
print("\n🧪 [مرحله ۴]: تست نهایی موتور ریاضی...")
time.sleep(5)
try:
    with urllib.request.urlopen("https://elen-backend-v2.onrender.com/openapi.json", timeout=15) as api_resp:
        if '"/api/math/discover"' in api_resp.read().decode('utf-8'):
            print("\n==================================================")
            print("🎉 [پیروزی نهایی]: همه چیز خودکار درست شد و موتور ریاضی فعال شد!")
            print("👉 حالا به سایت بروید و دکمه 'اجرای کشف' را تست کنید.")
            print("==================================================")
        else:
            print("⚠️ سرور Live است اما مسیر ریاضی پیدا نشد.")
except Exception as e:
    print(f"⚠️ خطا در تست: {e}")
