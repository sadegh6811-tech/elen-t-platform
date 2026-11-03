#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - Step-by-Step Smart Fix Module (V10)
# ==========================================================

set -e # توقف ربات در صورت بروز خطای غیرمنتظره
PROJECT_DIR=~/Nazi/auth-portal
PINGGY_URL="https://oedaa-37-187-56-56.run.pinggy-free.link"

echo "🎓 شروع آموزش ربات..."
sleep 1

# ----------------------------------------------------------
# گام ۱: پاکسازی کامل محیط (Nuke & Pave)
# ----------------------------------------------------------
echo "🧹 گام ۱: پاکسازی فایل‌های خراب و محلی..."
cd $PROJECT_DIR
rm -rf node_modules dist .vercel package-lock.json .vercelignore vercel.json
npm pkg delete overrides dependencies.rollup devDependencies.rollup 2>/dev/null || true

# ----------------------------------------------------------
# گام ۲: بازنویسی فایل‌های پیکربندی استاندارد (Zero-Config)
# ----------------------------------------------------------
echo "⚙️ گام ۲: ساخت فایل‌های پیکربندی استاندارد..."

cat << 'PKG' > package.json
{
  "name": "elen-auth-portal",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.2.0",
    "typescript": "^5.2.2"
  }
}
PKG

cat << 'TS' > tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true
  },
  "include": ["src"]
}
TS

# ----------------------------------------------------------
# گام ۳: بازنویسی کدهای React با ساختار فوق‌تمیز
# ----------------------------------------------------------
echo "📝 گام ۳: بازنویسی کدهای React (بدون هیچ خطای سینتکسی)..."

cat << 'HTML' > index.html
<!doctype html>
<html lang="fa" dir="rtl">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ELEN Secure Terminal</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
HTML

cat << 'MAIN' > src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
MAIN

cat << 'APP' > src/App.tsx
import AuthCard from './components/AuthCard';

export default function App() {
  return (
    <div className="min-h-screen bg-[#0B0A1A] flex items-center justify-center p-4">
      <AuthCard />
    </div>
  );
}
APP

cat << 'AUTH' > src/components/AuthCard.tsx
import { useState } from 'react';

export default function AuthCard() {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [msg, setMsg] = useState('');

  // لینک بک‌اند مستقیماً اینجا قرار گرفته تا وابسته به .env نباشد
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg('Connecting...');
    try {
      const res = await fetch(API_URL + '/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user, password: pass })
      });
      const data = await res.json();
      setMsg(data.success ? '✅ Success!' : '❌ Access Denied');
    } catch (err) {
      setMsg('⚠️ Network Error');
    }
  };

  return (
    <div className="bg-[#110e2d] p-8 rounded-xl w-full max-w-sm border border-cyan-500 shadow-2xl text-white">
      <h2 className="text-2xl mb-6 text-center font-bold">ELEN Terminal</h2>
      <form onSubmit={handleLogin} className="space-y-4 text-right">
        <input 
          type="text" 
          placeholder="نام کاربری" 
          onChange={(e) => setUser(e.target.value)} 
          className="w-full bg-black/50 border border-gray-600 p-3 rounded text-left" 
          required
        />
        <input 
          type="password" 
          placeholder="رمز عبور" 
          onChange={(e) => setPass(e.target.value)} 
          className="w-full bg-black/50 border border-gray-600 p-3 rounded text-left" 
          required
        />
        <button type="submit" className="w-full bg-cyan-600 p-3 rounded font-bold hover:bg-cyan-500">
          آغاز فرآیند
        </button>
      </form>
      {msg && <p className="text-center mt-4 text-sm">{msg}</p>}
    </div>
  );
}
AUTH

# ----------------------------------------------------------
# گام ۴: تنظیم متغیر محیطی در ورسل از طریق CLI
# ----------------------------------------------------------
echo "🔗 گام ۴: تزریق لینک Pinggy به ورسل..."
echo "$PINGGY_URL" | vercel env add VITE_API_URL production --force > /dev/null 2>&1 || true

# ----------------------------------------------------------
# گام ۵: ارسال به ورسل (فقط سورس کدها، بدون فایل‌های گوشی)
# ----------------------------------------------------------
echo "🚀 گام ۵: ارسال به Vercel و اجبار به بیلد در سرور..."
vercel --prod --yes --force > deploy_result.log 2>&1

# ----------------------------------------------------------
# گام ۶: بررسی نتیجه و استخراج خطا (اگر وجود داشته باشد)
# ----------------------------------------------------------
if grep -q "Error" deploy_result.log; then
    echo "❌ ربات با خطا مواجه شد. در حال استخراج لاگ دقیق..."
    DEPLOY_URL=$(grep -o 'https://auth-portal-[a-z0-9]*-sadegh6811.vercel.app' deploy_result.log | head -n 1)
    if [ -n "$DEPLOY_URL" ]; then
        vercel inspect "$DEPLOY_URL" --logs | grep -i "error" -A 5
    else
        cat deploy_result.log
    fi
    exit 1
else
    echo "🏆 پیروزی! ربات پروژه را با موفقیت دیپلوی کرد."
    grep -E "Production|Aliased" deploy_result.log
fi
