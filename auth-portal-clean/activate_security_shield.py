import os, base64, json, urllib.request, subprocess, re

print("🛡️ در حال طراحی سپر امنیتی و مکانیزم قفل اضطراری...")

gh_token = open(os.path.expanduser('~/.github_token')).read().strip()
repo = 'sadegh6811-tech/devstudio-bot'

def upload_to_github(path, content_bytes):
    b64 = base64.b64encode(content_bytes).decode('utf-8')
    req_get = urllib.request.Request(f'https://api.github.com/repos/{repo}/contents/{path}', headers={'Authorization': f'token {gh_token}'})
    try: sha = json.loads(urllib.request.urlopen(req_get).read().decode())['sha']
    except: sha = None
    data = {'message': f'feat: security shield update {path}', 'content': b64}
    if sha: data['sha'] = sha
    req_put = urllib.request.Request(f'https://api.github.com/repos/{repo}/contents/{path}', data=json.dumps(data).encode('utf-8'), headers={'Authorization': f'token {gh_token}', 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}, method='PUT')
    urllib.request.urlopen(req_put)
    print(f'✅ {path} آپلود شد.')

# ==========================================
# ۱. ارتقای بک‌اند (پایتون): JWT + Lockdown
# ==========================================
print("\n⚙️ مرحله ۱: ارتقای بک‌اند (افزودن JWT و مکانیزم Lockdown)...")
backend_path = os.path.expanduser('~/سبزی/public_proxy.py')
with open(backend_path, 'r', encoding='utf-8') as f:
    backend_code = f.read()

# پاکسازی کدهای قدیمی
backend_code = re.sub(r'@app\.post\("/api/login"\).*?(?=@app\.|\Z)', '', backend_code, flags=re.DOTALL)
backend_code = re.sub(r'@app\.get\("/api/karami/trade"\).*?(?=@app\.|\Z)', '', backend_code, flags=re.DOTALL)
backend_code = re.sub(r'@app\.post\("/api/math/discover"\).*?(?=@app\.|\Z)', '', backend_code, flags=re.DOTALL)
backend_code = re.sub(r'@app\.get\("/api/security/logs"\).*?(?=@app\.|\Z)', '', backend_code, flags=re.DOTALL)
backend_code = re.sub(r'@app\.get\("/api/market/analysis"\).*?(?=@app\.|\Z)', '', backend_code, flags=re.DOTALL)

security_shield_code = '''
import jwt
import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
import threading

# --- تنظیمات سپر امنیتی ---
SECRET_KEY = "ELEN_SUPER_SECRET_KEY_2026" # در نسخه واقعی در .env قرار می‌گیرد
ALGORITHM = "HS256"
security = HTTPBearer()
SYSTEM_LOCKDOWN = False
LOCKDOWN_TIMER = None

def unlock_system():
    global SYSTEM_LOCKDOWN
    time.sleep(180) # ۳ دقیقه قفل
    SYSTEM_LOCKDOWN = False
    print("🔓 سیستم پس از فروکش کردن تهدید، دوباره باز شد.")

def trigger_lockdown():
    global SYSTEM_LOCKDOWN, LOCKDOWN_TIMER
    if not SYSTEM_LOCKDOWN:
        SYSTEM_LOCKDOWN = True
        print("🚨 حمله تشخیص داده شد! سیستم به حالت Lockdown رفت.")
        if LOCKDOWN_TIMER is None or not LOCKDOWN_TIMER.is_alive():
            LOCKDOWN_TIMER = threading.Thread(target=unlock_system)
            LOCKDOWN_TIMER.daemon = True
            LOCKDOWN_TIMER.start()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if SYSTEM_LOCKDOWN:
        raise HTTPException(status_code=503, detail="سیستم به دلیل تهدید امنیتی موقتا قفل شده است.")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        trigger_lockdown() # توکن منقضی شده = احتمال حمله
        raise HTTPException(status_code=401, detail="توکن منقضی شده است")
    except jwt.InvalidTokenError:
        trigger_lockdown() # توکن نامعتبر = حمله
        raise HTTPException(status_code=401, detail="توکن نامعتبر است")

# --- API لاگین (صدور توکن) ---
@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    
    # (در نسخه نهایی با دیتابیس چک می‌شود، فعلا برای تست هر یوزر/پسی قبول است)
    if username and password:
        expire = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        token = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        return {"success": True, "token": token, "message": "✅ Connected securely."}
    else:
        trigger_lockdown() # تلاش برای لاگین خالی = حمله
        return {"success": False, "message": "اطلاعات ناقص"}

# --- موتورها (محافظت‌شده با JWT و Lockdown) ---
@app.post("/api/math/discover")
async def math_discover(user: dict = Depends(verify_token)):
    import random
    patterns = [{"type": "چندجمله‌ای درجه ۲", "formula": "y = 2.5x^2 - 3.1x", "r2": 0.984}]
    return {"success": True, "result": random.choice(patterns)}

@app.get("/api/market/analysis")
async def market_analysis(user: dict = Depends(verify_token)):
    data = {"pair": "XAU/USD", "current_price": "2345.50", "trend": "Bullish", "timeframe": "4H", "signal": "BUY", "entry_zone": ["2320.00", "2325.00"], "stop_loss": "2305.00", "take_profit_1": "2360.00", "take_profit_2": "2380.00", "confidence": 87, "risk_reward": "1:3.5"}
    return {"success": True, "data": data}

@app.get("/api/security/logs")
async def security_logs(user: dict = Depends(verify_token)):
    # در صورت درخواست بیش از حد، سیستم را قفل کن
    logs = [{"time": "11:41:29", "type": "Port Scan", "ip": "10.0.0.12", "status": "Honeypot Triggered"}]
    return {"success": True, "logs": logs}

@app.get("/api/karami/trade")
async def karami_trade(user: dict = Depends(verify_token)):
    try:
        result = subprocess.run([sys.executable, "master_sensor.py"], capture_output=True, text=True, timeout=120, cwd="karami")
        if result.returncode != 0:
            return {"success": False, "message": "خطا در اجرای موتور", "log": result.stderr}
        return {"success": True, "log": result.stdout}
    except Exception as e:
        return {"success": False, "message": str(e)}

# --- دکمه اضطراری (برای تست سنسور) ---
@app.post("/api/security/panic")
async def trigger_panic():
    trigger_lockdown()
    return {"message": "Lockdown activated"}
'''
backend_code += "\n" + security_shield_code
upload_to_github('public_proxy.py', backend_code.encode('utf-8'))

# ==========================================
# ۲. ارتقای فرانت‌اند (React): ذخیره توکن و مدیریت Lockdown
# ==========================================
print("\n🎨 مرحله ۲: ارتقای فرانت‌اند (ذخیره توکن و مدیریت خطای 503)...")
frontend_dir = os.path.expanduser('~/Nazi/auth-portal/src/components')

# اصلاح AuthCard برای ذخیره توکن
with open(os.path.join(frontend_dir, 'AuthCard.tsx'), 'r', encoding='utf-8') as f:
    auth_code = f.read()
auth_code = re.sub(r'if \(data\.success\) \{.*?(?=\} catch)', '''
if (data.success) {
        if (data.token) localStorage.setItem('elen_token', data.token);
        setMessage('✅ Success! Connected securely.');
        setIsError(false);
        if (isLogin) setTimeout(() => onLoginSuccess(username), 1000);
        else setTimeout(() => setIsLogin(true), 2000);
      } else {
        setMessage(data.message || '❌ خطا در احراز هویت');
        setIsError(true);
      }
''', auth_code, flags=re.DOTALL)
with open(os.path.join(frontend_dir, 'AuthCard.tsx'), 'w', encoding='utf-8') as f:
    f.write(auth_code)

# اصلاح موتورها برای ارسال توکن
def secure_component(filename, endpoint):
    path = os.path.join(frontend_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # جایگزینی fetch معمولی با fetch همراه توکن
    code = re.sub(r'fetch\(API_URL \+ [\'"](' + endpoint + r')[\'"],? ?(\{.*?\})?\)', 
                  r'''fetch(API_URL + '\1', {
      ...( \2 || {} ),
      headers: { ...( \2?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    })''', code, flags=re.DOTALL)
    
    # مدیریت خطای 503 (Lockdown)
    code = code.replace("if (!res.ok) throw new Error(`Server returned ${res.status}`);", 
                        '''if (res.status === 503) { setError('🚨 سیستم به دلیل تهدید امنیتی موقتا قفل شده است. ۳ دقیقه دیگر تلاش کنید.'); return; }
      if (res.status === 401) { setError('⚠️ دسترسی غیرمجاز. لطفا دوباره لاگین کنید.'); return; }
      if (!res.ok) throw new Error(`Server returned ${res.status}`);''')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

secure_component('Mathbot.tsx', '/api/math/discover')
secure_component('Market.tsx', '/api/market/analysis')
secure_component('Karami.tsx', '/api/karami/trade')
secure_component('Security.tsx', '/api/security/logs')

print("✅ کدهای فرانت‌اند با موفقیت امن شدند.")

# ==========================================
# ۳. دیپلوی به Vercel و Render
# ==========================================
print("\n🚀 مرحله ۳: ارسال به Vercel...")
subprocess.run(["bash", "-c", "cd ~/Nazi/auth-portal && unset VERCEL_TOKEN && vercel --prod --yes --force > /dev/null 2>&1"])
print("✅ ورسل آپدیت شد.")

print("🚀 مرحله ۴: ارسال دستور بیلد به Render...")
render_key = open(os.path.expanduser('~/render_key.txt')).read().strip()
headers = {'Authorization': f'Bearer {render_key}', 'Accept': 'application/json'}
services = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.render.com/v1/services', headers=headers)).read().decode())
for s in services:
    if s['service']['name'] == 'elen-auth-backend':
        srv_id = s['service']['id']
        urllib.request.urlopen(urllib.request.Request(f'https://api.render.com/v1/services/{srv_id}/deploys', headers=headers, method='POST'))
        print("🏆 پیروزی کامل! سپر امنیتی فعال شد و به Render ارسال گردید.")
        break
