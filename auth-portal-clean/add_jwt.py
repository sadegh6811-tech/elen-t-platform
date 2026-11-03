import base64, json, urllib.request, os

gh_token = open(os.path.expanduser('~/.github_token')).read().strip()
repo = 'sadegh6811-tech/elen-t-platform'

print("📦 در حال اضافه کردن PyJWT به لیست پکیج‌ها...")
reqs = b"fastapi\nuvicorn\npandas\nrequests\npython-multipart\npydantic\nnumpy\nscikit-learn\nmatplotlib\nyfinance\nPyJWT\n"

b64 = base64.b64encode(reqs).decode('utf-8')
req_get = urllib.request.Request(f'https://api.github.com/repos/{repo}/contents/requirements.txt', headers={'Authorization': f'token {gh_token}'})
try: sha = json.loads(urllib.request.urlopen(req_get).read().decode())['sha']
except: sha = None

data = {'message': 'fix: add PyJWT to requirements', 'content': b64}
if sha: data['sha'] = sha

req_put = urllib.request.Request(f'https://api.github.com/repos/{repo}/contents/requirements.txt', data=json.dumps(data).encode('utf-8'), headers={'Authorization': f'token {gh_token}', 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}, method='PUT')
urllib.request.urlopen(req_put)
print("✅ requirements.txt آپدیت شد.")

print("🚀 ارسال دستور بیلد مجدد به Render...")
render_key = open(os.path.expanduser('~/render_key.txt')).read().strip()
headers = {'Authorization': f'Bearer {render_key}', 'Accept': 'application/json'}
services = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.render.com/v1/services', headers=headers)).read().decode())
for s in services:
    if s['service']['name'] == 'elen-auth-backend':
        srv_id = s['service']['id']
        urllib.request.urlopen(urllib.request.Request(f'https://api.render.com/v1/services/{srv_id}/deploys', headers=headers, method='POST'))
        print("🏆 تمام شد! ۳ دقیقه صبر کنید تا سرور آلمان آماده شود.")
        break
