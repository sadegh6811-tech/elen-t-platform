import base64, json, urllib.request, os, re

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

print("📤 1. در حال آپلود دیتای فارکس...")
with open(os.path.expanduser('~/karami/data_EURUSD_1m.csv'), 'rb') as f:
    upload_to_github('karami/data_EURUSD_1m.csv', f.read())

print("📤 2. در حال آپلود لیست پکیج‌ها...")
reqs = b"fastapi\nuvicorn\npandas\nrequests\npython-multipart\npydantic\nnumpy\nscikit-learn\nmatplotlib\nyfinance\n"
upload_to_github('requirements.txt', reqs)

print("📤 3. در حال اصلاح کد بک‌اند و آپلود...")
with open(os.path.expanduser('~/سبزی/public_proxy.py'), 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'@app\.get\("/api/karami/trade"\).*?(?=@app\.|\Z)', '', content, flags=re.DOTALL)

karami_code = '''
import subprocess
import sys

@app.get("/api/karami/trade")
async def karami_trade():
    try:
        # اجرا با تنظیم پوشه کاری روی karami
        result = subprocess.run([sys.executable, "master_sensor.py"], capture_output=True, text=True, timeout=120, cwd="karami")
        if result.returncode != 0:
            return {"success": False, "message": "خطا در اجرای موتور", "log": result.stderr}
        return {"success": True, "log": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e)}
'''
content += "\n" + karami_code
upload_to_github('public_proxy.py', content.encode('utf-8'))

print("🚀 4. ارسال دستور بیلد مجدد به Render...")
render_key = open(os.path.expanduser('~/render_key.txt')).read().strip()
headers = {'Authorization': f'Bearer {render_key}', 'Accept': 'application/json'}
services = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.render.com/v1/services', headers=headers)).read().decode())
for s in services:
    if s['service']['name'] == 'elen-auth-backend':
        srv_id = s['service']['id']
        urllib.request.urlopen(urllib.request.Request(f'https://api.render.com/v1/services/{srv_id}/deploys', headers=headers, method='POST'))
        print("🏆 تمام شد! دستور بیلد مجدد صادر شد.")
        break
