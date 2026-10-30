import os
import io
import time
import requests
import pandas as pd
from collections import defaultdict
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ایمپورت سیستم امنیتی که ساختیم
from security_sensor import SecuritySensor
from security_engine import SecurityEngine

app = FastAPI(title="Elen-MathBot Public Gateway (Secured)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["POST", "GET"], allow_headers=["*"])

# متغیرهای محیطی
PUBLIC_DEMO_KEY = os.getenv("PUBLIC_DEMO_KEY", "demo-public")
SHADOW_CORE_URL = os.getenv("SHADOW_CORE_URL", "http://127.0.0.1:8001")
SHADOW_SECRET = os.getenv("SHADOW_SECRET", "shadow-core-secret-2024")

# راه‌اندازی سنسور و موتور امنیتی
sensor = SecuritySensor()
engine = SecurityEngine()

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """لایه امنیتی: هر درخواست قبل از رسیدن به روت اصلی بررسی می‌شود"""
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    method = request.method
    
    # بدنه درخواست را می‌خوانیم (برای تحلیل)
    body = await request.body()
    body_text = body.decode('utf-8', errors='ignore')
    
    # ۱. تحلیل با سنسور
    signals = sensor.analyze(client_ip, path, body_text)
    
    # ۲. به‌روزرسانی وضعیت
    level = sensor.update(signals)
    
    if signals:
        print(f"🚨 حمله شناسایی شد از {client_ip} در {path}")
        for sig in signals:
            print(f"   - {sig['type']} (شدت {sig['severity']})")
            
    if level >= 1:
        engine.respond(level, f"حمله از {client_ip}: {[s['type'] for s in signals]}")
    
    # ۳. اجرای واکنش بر اساس سطح
    if level == 3:
        print(f"🚨 سطح ۳: رد درخواست از {client_ip} (قفل کامل)")
        return JSONResponse(
            {"status": "maintenance", "message": "System temporarily unavailable"},
            status_code=503
        )
    
    if level == 2:
        print(f"🌑 سطح ۲: ارسال پاسخ honeypot به {client_ip}")
        return JSONResponse({
            "status": "success",
            "formula": "y = x1 + x2", 
            "r2_score": 0.42,
            "note": "This is a decoy response"
        })
    
    # ۴. اگر همه چیز عادی بود، درخواست را ادامه بده
    response = await call_next(request)
    return response

@app.post("/discover")
async def discover(request: Request, file: UploadFile = File(...), x_api_key: str = Header(None)):
    if x_api_key != PUBLIC_DEMO_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    try:
        contents = await file.read()
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV accepted.")
            
        # اصلاح باگ: خواندن CSV در خط جدید
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        if len(df) > 5000:
            raise HTTPException(status_code=413, detail="Max 5000 rows.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")

    try:
        files = {"file": (file.filename, contents, "text/csv")}
        headers = {"X-Shadow-Token": SHADOW_SECRET}
        response = requests.post(f"{SHADOW_CORE_URL}/internal/discover", files=files, headers=headers, timeout=120)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Core error: {response.text}")
        return response.json()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Core engine timeout.")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Core engine offline.")

@app.get("/")
def root():
    return {"status": "online", "service": "Public Gateway (Secured)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, access_log=False)

# --- ELEN Auth Endpoint (Added via Deploy-Bot) ---


import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect('elen_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/api/register")
async def register(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return {"success": False, "message": "نام کاربری و رمز عبور الزامی است"}
        
        conn = sqlite3.connect('elen_users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            conn.close()
            return {"success": False, "message": "این نام کاربری قبلا ثبت شده است"}
        
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return {"success": True, "message": "ثبت‌نام با موفقیت انجام شد"}
    except Exception as e:
        return {"success": False, "message": str(e)}



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
