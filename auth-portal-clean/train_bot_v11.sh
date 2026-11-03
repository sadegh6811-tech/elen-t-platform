#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - V11 (Resilient Build & Debug)
# ==========================================================

PROJECT_DIR=~/Nazi/auth-portal
PINGGY_URL="https://oedaa-37-187-56-56.run.pinggy-free.link"

echo "🎓 شروع آموزش ربات (V11)..."

cd $PROJECT_DIR || { echo "❌ پوشه پیدا نشد"; exit 1; }

# پاکسازی
rm -rf node_modules dist .vercel package-lock.json
echo "🧹 محیط پاکسازی شد."

# ساخت فایل‌های استاندارد (همان کدهای تمیز قبلی)
cat << 'PKG' > package.json
{
  "name": "elen-auth-portal",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": { "build": "vite build" },
  "dependencies": { "react": "^18.2.0", "react-dom": "^18.2.0" },
  "devDependencies": { "@vitejs/plugin-react": "^4.2.1", "vite": "^5.2.0" }
}
PKG

cat << 'HTML' > index.html
<!doctype html>
<html lang="fa" dir="rtl">
  <head><meta charset="UTF-8" /><title>ELEN</title></head>
  <body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body>
</html>
HTML

mkdir -p src/components

cat << 'MAIN' > src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>)
MAIN

cat << 'APP' > src/App.tsx
import AuthCard from './components/AuthCard';
export default function App() {
  return <div className="min-h-screen bg-[#0B0A1A] flex items-center justify-center p-4"><AuthCard /></div>;
}
APP

cat << 'AUTH' > src/components/AuthCard.tsx
import { useState } from 'react';
export default function AuthCard() {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [msg, setMsg] = useState('');
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg('Connecting...');
    try {
      const res = await fetch(API_URL + '/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: user, password: pass }) });
      const data = await res.json();
      setMsg(data.success ? '✅ Success!' : '❌ Access Denied');
    } catch (err) { setMsg('⚠️ Network Error'); }
  };
  return (
    <div className="bg-[#110e2d] p-8 rounded-xl w-full max-w-sm border border-cyan-500 shadow-2xl text-white">
      <h2 className="text-2xl mb-6 text-center font-bold">ELEN Terminal</h2>
      <form onSubmit={handleLogin} className="space-y-4 text-right">
        <input type="text" placeholder="نام کاربری" onChange={(e) => setUser(e.target.value)} className="w-full bg-black/50 border border-gray-600 p-3 rounded text-left" required />
        <input type="password" placeholder="رمز عبور" onChange={(e) => setPass(e.target.value)} className="w-full bg-black/50 border border-gray-600 p-3 rounded text-left" required />
        <button type="submit" className="w-full bg-cyan-600 p-3 rounded font-bold hover:bg-cyan-500">آغاز فرآیند</button>
      </form>
      {msg && <p className="text-center mt-4 text-sm">{msg}</p>}
    </div>
  );
}
AUTH

# تنظیم لینک بک‌اند
echo "$PINGGY_URL" | vercel env add VITE_API_URL production --force > /dev/null 2>&1 || true
echo "🔗 لینک بک‌اند تنظیم شد."

# ارسال به ورسل (این بار با || true که باعث می‌شود ربات کرش نکند)
echo "🚀 در حال ارسال به Vercel (منتظر بمانید)..."
vercel --prod --yes --force > deploy_result.log 2>&1 || true

# بررسی نتیجه
if grep -q "Error" deploy_result.log; then
    echo "❌ ورسل در زمان بیلد خطا داد! لاگ دقیق خطا در زیر آمده است:"
    echo "--------------------------------------------------"
    grep -i "error" deploy_result.log -A 5 | tail -n 20
    echo "--------------------------------------------------"
    exit 1
else
    echo "🏆 پیروزی! بیلد در سرور ورسل با موفقیت انجام شد."
    grep -E "Production|Aliased" deploy_result.log
fi
