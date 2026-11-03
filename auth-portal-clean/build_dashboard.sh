#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🎨 ELEN Dashboard & Routing Module
# ==========================================================

echo "🚀 ربات در حال ساخت داشبورد و اعمال تغییرات..."

cd ~/Nazi/auth-portal || { echo "❌ پوشه پیدا نشد"; exit 1; }

# ۱. ساخت کامپوننت داشبورد
echo "🖥️ مرحله ۱: ساخت صفحه داشبورد..."
cat << 'TSX' > src/components/Dashboard.tsx
export default function Dashboard({ username, onLogout }: { username: string, onLogout: () => void }) {
  return (
    <div className="z-10 w-full max-w-4xl px-4 pt-10 flex flex-col items-center">
      {/* هدر داشبورد */}
      <div className="w-full flex justify-between items-center mb-10 bg-[#110e2d]/60 backdrop-blur-xl border border-cyan-500/30 p-4 rounded-2xl shadow-lg">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 flex items-center justify-center text-xl font-bold text-white shadow-lg shadow-cyan-500/50">
            {username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-xl font-bold text-white font-vazirmatn">خوش آمدید، {username}</h2>
            <p className="text-sm text-cyan-400 font-vazirmatn flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              متصل به هسته مرکزی ELEN
            </p>
          </div>
        </div>
        <button onClick={onLogout} className="px-4 py-2 bg-red-500/20 text-red-400 border border-red-500/50 rounded-lg hover:bg-red-500/30 transition-colors text-sm font-vazirmatn">
          خروج از حساب
        </button>
      </div>

      {/* کارت‌های موتورها */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
        {/* موتور اول */}
        <div className="bg-[#110e2d]/60 backdrop-blur-xl border border-white/10 p-6 rounded-2xl hover:border-cyan-400/50 transition-all cursor-pointer group">
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">🧮</div>
          <h3 className="text-lg font-bold text-white font-vazirmatn mb-2">موتور محاسباتی</h3>
          <p className="text-sm text-gray-400 font-vazirmatn">دسترسی به Mathbot و پردازش‌های فیزیکی و مداری.</p>
        </div>

        {/* موتور دوم */}
        <div className="bg-[#110e2d]/60 backdrop-blur-xl border border-white/10 p-6 rounded-2xl hover:border-purple-400/50 transition-all cursor-pointer group">
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">🛡️</div>
          <h3 className="text-lg font-bold text-white font-vazirmatn mb-2">سنسور امنیتی</h3>
          <p className="text-sm text-gray-400 font-vazirmatn">پایش زنده حملات و تحلیل Honeypot در سرور.</p>
        </div>

        {/* موتور سوم */}
        <div className="bg-[#110e2d]/60 backdrop-blur-xl border border-white/10 p-6 rounded-2xl hover:border-green-400/50 transition-all cursor-pointer group">
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">📊</div>
          <h3 className="text-lg font-bold text-white font-vazirmatn mb-2">تحلیل بازار</h3>
          <p className="text-sm text-gray-400 font-vazirmatn">نمودارها و الگوریتم‌های مالی و Forex.</p>
        </div>
      </div>
    </div>
  );
}
TSX

# ۲. تغییر AuthCard برای انتقال به داشبورد
echo "🔗 مرحله ۲: اتصال فرم لاگین به داشبورد..."
cat << 'TSX' > src/components/AuthCard.tsx
import { useState } from 'react';

export default function AuthCard({ onLoginSuccess }: { onLoginSuccess: (username: string) => void }) {
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
        if (isLogin) {
          setTimeout(() => onLoginSuccess(username), 1000); // انتقال به داشبورد
        } else {
          setTimeout(() => setIsLogin(true), 2000); 
        }
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

# ۳. آپدیت App برای مدیریت وضعیت لاگین
echo "🎬 مرحله ۳: به‌روزرسانی چیدمان اصلی..."
cat << 'TSX' > src/App.tsx
import { useState } from 'react';
import Starfield from './components/Starfield';
import Logo from './components/Logo';
import AuthCard from './components/AuthCard';
import Dashboard from './components/Dashboard';

export default function App() {
  const [loggedInUser, setLoggedInUser] = useState<string | null>(null);

  return (
    <div className="relative min-h-screen bg-[#0B0A1A] overflow-hidden flex flex-col items-center justify-center font-vazirmatn">
      <Starfield />
      {!loggedInUser ? (
        <div className="z-10 flex flex-col items-center w-full px-4 pt-10">
          <Logo />
          <AuthCard onLoginSuccess={(user) => setLoggedInUser(user)} />
        </div>
      ) : (
        <Dashboard username={loggedInUser} onLogout={() => setLoggedInUser(null)} />
      )}
    </div>
  );
}
TSX

# ۴. دیپلوی روی Vercel
echo "🚀 مرحله ۴: ارسال به Vercel..."
unset VERCEL_TOKEN
vercel --prod --yes --force > deploy_dashboard.log 2>&1

if grep -q "Ready in" deploy_dashboard.log; then
    echo "🏆🏆🏆 پیروزی کامل! داشبورد با موفقیت ساخته و مستقر شد."
    echo "🌐 لینک شما: https://auth-portal-ruby.vercel.app"
else
    echo "⚠️ ورسل آپدیت شد اما لاگ را بررسی کنید."
    tail -n 10 deploy_dashboard.log
fi
