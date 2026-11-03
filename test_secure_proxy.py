#!/usr/bin/env python3
"""
تست یکپارچه‌سازی سنسور امنیتی با FastAPI
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from security_sensor import SecuritySensor
from security_engine import SecurityEngine
import uvicorn
from pathlib import Path

app = FastAPI()
sensor = SecuritySensor()
engine = SecurityEngine()

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # ۱. استخراج اطلاعات
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    body = await request.body()
    
    # ۲. تحلیل با سنسور
    signals = sensor.analyze(client_ip, path, body.decode('utf-8', errors='ignore'))
    
    # ۳. به‌روزرسانی وضعیت و واکنش
    level = sensor.update(signals)
    
    if signals:
        print(f"🚨 حمله شناسایی شد از {client_ip} در {path}")
        for sig in signals:
            print(f"   - {sig['type']} (شدت {sig['severity']})")
            
    if level >= 1:
        engine.respond(level, f"حمله از {client_ip}: {[s['type'] for s in signals]}")
    
    # ۴. اجرای واکنش بر اساس سطح
    if level == 3:
        return JSONResponse(
            {"status": "maintenance", "message": "System temporarily unavailable"},
            status_code=503
        )
    
    if level == 2:
        # حالت سایه: پاسخ جعلی
        print(f"🌑 حالت سایه: ارسال پاسخ honeypot به {client_ip}")
        return JSONResponse({
            "status": "success",
            "formula": "y = x1 + x2",
            "r2_score": 0.42,
            "note": "This is a decoy response"
        })
    
    # ۵. درخواست‌های عادی
    response = await call_next(request)
    return response

@app.get("/")
def root():
    return {"status": "ok", "message": "ELEN-T Secure Proxy Test"}

@app.post("/discover")
async def discover():
    return {"status": "success", "message": "Discovery engine running"}

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 سرور تست امنیتی راه‌اندازی شد")
    print("=" * 60)
    print("🔗 http://127.0.0.1:9000")
    print("⚠️  برای توقف: Ctrl+C")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=9000)
