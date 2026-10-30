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

@app.post("/api/login")
async def login(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        conn = sqlite3.connect('elen_users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
        user = c.fetchone()
        conn.close()
        
        if user:
            return {"success": True, "message": "✅ Connected to ELEN Core successfully!"}
        else:
            return {"success": False, "message": "نام کاربری یا رمز عبور اشتباه است"}
    except Exception as e:
        return {"success": False, "message": str(e)}


import random

@app.post("/api/math/discover")
async def math_discover(request: Request):
    try:
        # شبیه‌سازی موتور کشف (در نسخه واقعی، اینجا به Mathbot شما وصل می‌شود)
        patterns = [
            {"type": "چندجمله‌ای درجه ۲ (سهمی)", "formula": "y = 2.5x^2 - 3.1x + 4.0", "r2": 0.984},
            {"type": "تابع مثلثاتی (سینوسی)", "formula": "y = 1.5 * sin(2.3x)", "r2": 0.951},
            {"type": "تابع نمایی", "formula": "y = 0.8 * e^(0.4x)", "r2": 0.992},
            {"type": "تابع لگاریتمی", "formula": "y = 3.2 * log(x) + 1.1", "r2": 0.913},
            {"type": "چندجمله‌ای درجه ۱ (خطی)", "formula": "y = 4.5x - 2.0", "r2": 0.999}
        ]
        result = random.choice(patterns)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "message": str(e)}


import random
from datetime import datetime

@app.get("/api/security/logs")
async def security_logs():
    try:
        # شبیه‌سازی لاگ‌های هانی‌پات (در نسخه واقعی به security_engine.py وصل می‌شود)
        logs = [
            {"time": datetime.now().strftime("%H:%M:%S"), "type": "SQL Injection", "ip": "192.168.1.45", "status": "Blocked"},
            {"time": datetime.now().strftime("%H:%M:%S"), "type": "Port Scan", "ip": "10.0.0.12", "status": "Honeypot Triggered"},
            {"time": datetime.now().strftime("%H:%M:%S"), "type": "Brute Force", "ip": "203.0.113.88", "status": "Blocked"},
            {"time": datetime.now().strftime("%H:%M:%S"), "type": "Path Traversal", "ip": "198.51.100.7", "status": "Honeypot Triggered"}
        ]
        return {"success": True, "logs": random.sample(logs, k=random.randint(2, 4))}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.get("/api/market/analysis")
async def market_analysis():
    try:
        # شبیه‌سازی داده‌های تحلیل بازار
        data = {
            "pair": "XAU/USD",
            "price": "2345.50",
            "trend": "Bullish",
            "confidence": 87,
            "forecast": [2320, 2335, 2345, 2360, 2380],
            "recommendation": "Buy on dips"
        }
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "message": str(e)}
