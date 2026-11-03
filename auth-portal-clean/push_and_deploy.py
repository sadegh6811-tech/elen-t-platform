import os
import time
import urllib.request
import json
import base64

GITHUB_TOKEN_FILE = os.path.expanduser('~/.github_token')
API_KEY_FILE = os.path.expanduser('~/.render_api_key')
REPO = "sadegh6811-tech/devstudio-bot"
SERVICE_ID = "srv-dbje2lgae00c73dv3a20"

print("==================================================")
print("🤖 [ربات]: بررسی و آپلود فایل‌های ماژول‌های امنیتی...")
print("==================================================")

token = open(GITHUB_TOKEN_FILE, 'r').read().strip()
headers_gh = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}

files_to_check = ['security_sensor.py', 'security_engine.py']
files_found = []

for file in files_to_check:
    if os.path.exists(file):
        print(f"✅ فایل {file} پیدا شد. در حال آپلود به گیت‌هاب...")
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        url = f"https://api.github.com/repos/{REPO}/contents/{file}"
        
        try:
            req_get = urllib.request.Request(url, headers=headers_gh)
            try:
                sha = json.loads(urllib.request.urlopen(req_get).read().decode())['sha']
            except:
                sha = None
            
            data = {'message': f'feat: add {file}', 'content': b64}
            if sha: data['sha'] = sha
            
            req_put = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={**headers_gh, 'Content-Type': 'application/json'}, method='PUT')
            urllib.request.urlopen(req_put)
            files_found.append(file)
            print(f"✅ {file} با موفقیت در گیت‌هاب آپلود شد.")
        except Exception as e:
            print(f"⚠️ خطا در آپلود {file}: {e}")
    else:
        print(f"⚠️ فایل {file} روی گوشی پیدا نشد! (سرور ممکن است باز هم کرش کند)")

# مرحله ۲: ارسال دستور دیپلوی
print("\n🚀 [مرحله ۲]: ارسال دستور دیپلوی به Render...")
render_key = open(API_KEY_FILE, 'r').read().strip()
headers_render = {"Authorization": f"Bearer {render_key}", "Content-Type": "application/json", "Accept": "application/json"}
deploy_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
deploy_data = json.dumps({"clearCache": "clear"}).encode('utf-8')

try:
    req = urllib.request.Request(deploy_url, data=deploy_data, headers=headers_render, method='POST')
    with urllib.request.urlopen(req) as resp:
        print("✅ دیپلوی جدید با موفقیت ارسال شد!")
        print("👉 به داشبورد Render بروید و وضعیت را چک کنید.")
except Exception as e:
    print(f"❌ خطا در ارسال دیپلوی: {e}")
    print("👉 لطفا دکمه Manual Deploy را در Render به صورت دستی بزنید.")
