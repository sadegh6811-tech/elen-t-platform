import base64, json, urllib.request, os, subprocess

gh_token = open(os.path.expanduser('~/.github_token')).read().strip()
repo = 'sadegh6811-tech/elen-t-platform'

def upload_to_github(path, content_bytes):
    b64 = base64.b64encode(content_bytes).decode('utf-8')
    req_get = urllib.request.Request(f'https://api.github.com/repos/{repo}/contents/{path}', headers={'Authorization': f'token {gh_token}'})
    try: sha = json.loads(urllib.request.urlopen(req_get).read().decode())['sha']
    except: sha = None
    data = {'message': f'update {path}', 'content': b64}
    if sha: data['sha'] = sha
    req_put = urllib.request.Request(f'https://api.github.com/repos/{repo}/contents/{path}', data=json.dumps(data).encode('utf-8'), headers={'Authorization': f'token {gh_token}', 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}, method='PUT')
    urllib.request.urlopen(req_put)
    print(f'✅ {path} آپلود شد.')

print("📤 1. در حال آپلود تمام فایل‌های پایتون و دیتای کرمی به گیت‌هاب...")
karami_dir = os.path.expanduser('~/karami')
for file in os.listdir(karami_dir):
    if file.endswith(('.py', '.csv')):
        filepath = os.path.join(karami_dir, file)
        with open(filepath, 'rb') as f:
            upload_to_github(f'karami/{file}', f.read())

print("\n🎨 2. در حال اصلاح کد فرانت‌اند برای نمایش دقیق خطاها...")
frontend_path = os.path.expanduser('~/Nazi/auth-portal/src/components/Karami.tsx')
with open(frontend_path, 'r', encoding='utf-8') as f:
    content = f.read()

# اصلاح بخش نمایش لاگ خطا در فرانت‌اند
content = content.replace(
    "setError(data.message || 'خطا در اجرا');",
    "setError(data.message || 'خطا در اجرا');\n        if (data.log) setLog(data.log);"
)
with open(frontend_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ کد فرانت‌اند اصلاح شد.")

print("\n🚀 3. در حال ارسال کدهای جدید به Vercel...")
subprocess.run(["bash", "-c", "cd ~/Nazi/auth-portal && unset VERCEL_TOKEN && vercel --prod --yes --force > deploy_fix.log 2>&1"])
print("✅ ورسل آپدیت شد.")

print("\n🚀 4. ارسال دستور بیلد مجدد به Render...")
render_key = open(os.path.expanduser('~/render_key.txt')).read().strip()
headers = {'Authorization': f'Bearer {render_key}', 'Accept': 'application/json'}
services = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.render.com/v1/services', headers=headers)).read().decode())
for s in services:
    if s['service']['name'] == 'elen-auth-backend':
        srv_id = s['service']['id']
        urllib.request.urlopen(urllib.request.Request(f'https://api.render.com/v1/services/{srv_id}/deploys', headers=headers, method='POST'))
        print("🏆 تمام شد! تمام فایل‌ها و اصلاحات ارسال شدند.")
        break
