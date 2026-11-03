from quant_features import prepare_data
import os
import io
import time
import numpy as np
import pandas as pd
import sympy as sp
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, '/data/data/com.termux/files/home/sadegh')
try:
    from engine_v27_clean import gp_core_v27, evaluate_tree_safe, tree_to_sympy
except ImportError as e:
    print(f"❌ خطا در لود موتور GP: {e}")
    sys.exit(1)

app = FastAPI(title="Shadow Core", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["POST", "GET"], allow_headers=["*"])

SHADOW_TOKEN = os.getenv("SHADOW_SECRET", "shadow-core-secret-2024")

def verify_shadow_token(x_shadow_token: str = Header(None)):
    if not x_shadow_token or x_shadow_token != SHADOW_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/internal/discover")
async def internal_discover(file: UploadFile = File(None), x_shadow_token: str = Header(None)):
    verify_shadow_token(x_shadow_token)
    start_time = time.time()
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        cols = {str(c).lower(): c for c in df.columns}
        
        if 'close' not in cols or 'open' not in cols:
            raise ValueError("Need OHLC columns")
        
        close = df[cols['close']].values.astype(float)
        open_p = df[cols['open']].values.astype(float)
        high = df[cols['high']].values.astype(float) if 'high' in cols else close
        low = df[cols['low']].values.astype(float) if 'low' in cols else close
        
        n = len(close)
        if n < 100:
            raise ValueError("Need at least 100 candles")
        
        # ═══════════════════════════════════════════════════════
        # 🎯 هدف: نوسان ۵ کندل آینده (Future 5-candle ATR)
        # ═══════════════════════════════════════════════════════
        tr = np.maximum(high - low, 
                       np.maximum(np.abs(high - np.roll(close, 1)),
                                 np.abs(low - np.roll(close, 1))))
        tr[0] = high[0] - low[0]
        
        # ATR آینده (میانگین ۵ کندل بعد)
        future_volatility = np.zeros(n)
        for i in range(n - 5):
            future_volatility[i] = np.mean(tr[i+1:i+6])
        
        # ═══════════════════════════════════════════════════════
        # 🧠 ۱۲ ویژگی حرفه‌ای نوسان
        # ═══════════════════════════════════════════════════════
        def rolling_atr(h, l, c, window):
            tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
            tr[0] = h[0] - l[0]
            return pd.Series(tr).rolling(window).mean().bfill().values
        
        # ۱-۳. ATR در سه بازه (حافظه نوسان)
        atr_5 = rolling_atr(high, low, close, 5)
        atr_14 = rolling_atr(high, low, close, 14)
        atr_30 = rolling_atr(high, low, close, 30)
        
        # ۴. Parkinson Volatility (نوسان بر اساس High/Low)
        parkinson = (np.log(high / low + 1e-9) ** 2) / (4 * np.log(2))
        parkinson = pd.Series(parkinson).rolling(14).mean().bfill().values
        
        # ۵. Garman-Klass Volatility
        gk = 0.5 * (np.log(high / low + 1e-9) ** 2) - (2 * np.log(2) - 1) * (np.log(close / open_p + 1e-9) ** 2)
        gk = pd.Series(np.abs(gk)).rolling(14).mean().bfill().values
        
        # ۶. Body Size (اندازه بدنه)
        body = np.abs(close - open_p)
        body_avg = pd.Series(body).rolling(14).mean().bfill().values
        
        # ۷. Range Ratio (نسبت نوسان اخیر به میانگین)
        tr_series = pd.Series(tr)
        range_ratio = (tr_series / tr_series.rolling(30).mean()).fillna(1.0).values
        
        # ۸. RSI (شاخص قدرت نسبی)
        delta = np.diff(close, prepend=close[0])
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(14).mean().bfill().values
        avg_loss = pd.Series(loss).rolling(14).mean().bfill().values
        rs = avg_gain / (avg_loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))
        
        # ۹. Volatility Ratio (نوسان کوتاه/بلندمدت)
        vol_ratio = atr_5 / (atr_30 + 1e-9)
        
        # ۱۰. High-Low Range (نوسان خام)
        hl_range = (high - low) / (close + 1e-9)
        
        # ۱۱. Change (تغییر قیمت)
        change = (close - np.roll(close, 1)) / (np.roll(close, 1) + 1e-9)
        change[0] = 0
        
        # ۱۲. Absolute Return (قدرت مطلق حرکت)
        abs_return = np.abs(change)
        
        features_df, target_series = prepare_data(df)
        features = list(features_df.columns)
        X = features_df.values
        y = target_series.values
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data Error: {str(e)}")

    try:
        X_mean, X_std = X.mean(0), X.std(0) + 1e-9
        X_norm = (X - X_mean) / X_std
        y_mean, y_std = y.mean(), y.std() + 1e-9
        y_norm = (y - y_mean) / y_std
        
        split = int(len(X) * 0.8)
        X_tr, y_tr = X_norm[:split], y_norm[:split]
        X_val, y_val = X_norm[split:], y_norm[split:]
        y_val_raw = y[split:]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scaling Error: {str(e)}")

    try:
        np.random.seed(42)
        import random
        random.seed(42)
        # 🚀 قدرت بالا برای پیدا کردن الگوی نوسان
        tree, mse, a = gp_core_v27(X_tr, y_tr, features, 
                                    generations=150, 
                                    pop_size=400, 
                                    max_nodes=40)
        if tree is None: raise ValueError("GP Failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GP Error: {str(e)}")

    try:
        pred_val_norm = np.nan_to_num(evaluate_tree_safe(tree, X_val, features))
        pred_val_raw = (a * pred_val_norm) * y_std + y_mean
        var_y_val = np.sum((y_val_raw - np.mean(y_val_raw))**2)
        r2_val = 1 - np.sum((y_val_raw - pred_val_raw)**2) / (var_y_val + 1e-9)
        
        final_expr = a * tree_to_sympy(tree)
        final_expr = final_expr * sp.Float(y_std) + sp.Float(y_mean)
        simplified = sp.expand(final_expr)
        
        return {
            "status": "success",
            "mode": "shadow_pro",
            "target": "Future Volatility (5-candle ATR)",
            "formula": str(simplified),
            "mse": round(float(mse), 6),
            "r2": round(float(r2_val), 4),
            "samples_train": len(X_tr),
            "samples_test": len(X_val),
            "execution_time": round(time.time() - start_time, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eval Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, access_log=False)
