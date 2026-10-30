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
@app.post("/api/login")
async def elen_login(request: Request):
    try:
        data = await request.json()
        print(f"🔐 درخواست ورود دریافت شد: {data}")
        # سنسور امنیتی شما می‌تواند اینجا فعال شود
        return {"success": True, "message": "✅ Connected to ELEN Core successfully!"}
    except Exception as e:
        return {"success": False, "error": str(e)}
# -------------------------------------------------
