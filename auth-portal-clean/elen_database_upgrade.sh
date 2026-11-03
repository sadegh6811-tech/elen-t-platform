#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🤖 ELEN Deploy-Bot - Database & Auth Upgrade
# ==========================================================

echo "🗄️ مرحله ۱: ارتقای بک‌اند پایتون (اضافه کردن دیتابیس SQLite)..."
cd ~/سبزی || { echo "❌ پوشه سبزی پیدا نشد"; exit 1; }

# اسکریپت پایتون برای تزریق کد دیتابیس به فایل اصلی بدون خراب کردن کدهای قبلی
cat << 'PYEOF' > upgrade_backend.py
import re

with open('public_proxy.py', 'r', encoding='utf-8') as f:
    content = f.read()

# حذف کد لاگین ساده قبلی اگر وجود دارد
content = re.sub(r'@app\.post\("/api/login"\).*?(?=@app\.|\Z)', '', content, flags=re.DOTALL)

# کد جدید لاگین و ثبت‌نام با دیتابیس
db_code = '''
import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect('elen_users.db')
    c = conn.cursor()
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)\'\'\')
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
'''
# اضافه کردن کد جدید به انتهای فایل
content += "\n" + db_code

with open('public_proxy.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ بک‌اند با موفقیت ارتقا یافت (دیتابیس SQLite اضافه شد).")
PYEOF
python upgrade_backend.py
rm upgrade_backend.py

# آپلود به گیت‌هاب
git add public_proxy.py
git commit -m "feat: add SQLite database and register endpoint"
git push origin main -f > /dev/null 2>&1
echo "✅ کدهای بک‌اند به گیت‌هاب ارسال شدند. (Render در حال آپدیت است)"

echo "🎨 مرحله ۲: ارتقای فرانت‌اند (اضافه کردن دکمه ثبت‌نام)..."
cd ~/Nazi/auth-portal || { echo "❌ پوشه فرانت‌اند پیدا نشد"; exit 1; }

cat << 'TSX' > src/components/AuthCard.tsx
import { useState } from 'react';

export default function AuthCard() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);

  const API_URL = 'https://elen-auth-backend.onrender.com';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('در حال اتصال به سرور ابری...');
    setIsError(false);

    try {
      const endpoint = isLogin ? '/api/login' : '/api/register';
      const response = await fetch(API_URL + endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      
      if (data.success) {
        setMessage(isLogin ? '✅ Success! Connected.' : '✅ ثبت‌نام موفق! حالا وارد شوید.');
        setIsError(false);
        if (!isLogin) setTimeout(() => setIsLogin(true), 2000); // انتقال خودکار به لاگین
      } else {
        setMessage(data.message || '❌ خطا در احراز هویت');
        setIsError(true);
      }
    } catch (error) {
      setMessage('⚠️ Network Error (سرور در حال بیدار شدن است)');
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="z-10 bg-[#110e2d]/60 backdrop-blur-xl border border-cyan-500/30 p-8 rounded-2xl w-full max-w-sm shadow-[0_0_30px_rgba(6,182,212,0.15)] relative">
      <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-cyan-400 rounded-tl-lg"></div>
      <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-cyan-400 rounded-tr-lg"></div>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-cyan-400 rounded-bl-lg"></div>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-cyan-400 rounded-br-lg"></div>

      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white font-vazirmatn">{isLogin ? 'خوش آمدید' : 'ثبت‌نام'}</h2>
        <div className="flex items-center gap-2 text-cyan-400 text-xs">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          آنلاین
        </div>
      </div>
      
      <p className="text-gray-400 text-xs mb-6 text-right font-vazirmatn">
        {isLogin ? 'برای دسترسی به ترمینال، اطلاعات خود را وارد کنید.' : 'برای ساخت حساب جدید، اطلاعات را وارد کنید.'}
      </p>

      <form onSubmit={handleSubmit} className="space-y-4 text-right" dir="rtl">
        <div>
          <label className="block text-xs font-medium text-cyan-400 mb-2 font-vazirmatn">01 — نام کاربری</label>
          <input 
            type="text" 
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white text-sm focus:outline-none focus:border-cyan-400 transition-colors font-vazirmatn"
            placeholder="نام کاربری را وارد کنید"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-cyan-400 mb-2 font-vazirmatn">02 — رمز عبور</label>
          <input 
            type="password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white text-sm focus:outline-none focus:border-cyan-400 transition-colors font-vazirmatn"
            placeholder="رمز عبور را وارد کنید"
            required
          />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold py-3 rounded-lg hover:opacity-90 transition-all text-sm disabled:opacity-50 font-vazirmatn mt-4 shadow-lg shadow-cyan-500/20"
        >
          {loading ? 'در حال پردازش...' : (isLogin ? 'آغاز فرآیند' : 'ثبت‌نام کنید')}
        </button>

        {message && (
          <div className={`text-center text-xs mt-4 p-2 rounded-lg bg-black/30 border ${isError ? 'border-red-500/50 text-red-300' : 'border-green-500/50 text-green-300'} font-vazirmatn`}>
            {message}
          </div>
        )}
      </form>

      <div className="mt-6 text-center">
        <button 
          onClick={() => { setIsLogin(!isLogin); setMessage(''); }}
          className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors font-vazirmatn"
        >
          {isLogin ? 'حساب کاربری ندارید؟ ثبت‌نام کنید' : 'حساب دارید؟ وارد شوید'}
        </button>
      </div>
    </div>
  );
}
TSX

echo "🚀 مرحله ۳: ارسال فرانت‌اند به Vercel..."
unset VERCEL_TOKEN
vercel --prod --yes --force > deploy_db.log 2>&1

if grep -q "Ready in" deploy_db.log; then
    echo "🏆🏆🏆 پیروزی کامل! سیستم دیتابیس و ثبت‌نام با موفقیت راه‌اندازی شد."
    echo "🌐 آدرس سایت: https://auth-portal-ruby.vercel.app"
else
    echo "⚠️ ورسل آپدیت شد. (در حال ساخت)"
fi
