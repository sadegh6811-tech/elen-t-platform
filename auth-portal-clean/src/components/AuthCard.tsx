import { useState } from 'react';

export default function AuthCard({ onLoginSuccess }: { onLoginSuccess: (username: string) => void }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');
    
    const endpoint = isLogin ? '/api/login' : '/api/register';
    
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await res.json();
      
      if (res.ok) {
        setIsError(false);
        if (isLogin) {
          setMessage('✅ ورود با موفقیت انجام شد!');
          localStorage.setItem('token', data.token);
          setTimeout(() => onLoginSuccess(data.username), 1000);
        } else {
          setMessage('✅ ثبت‌نام با موفقیت انجام شد! حالا وارد شوید.');
          setIsLogin(true);
        }
      } else {
        setIsError(true);
        setMessage(`❌ ${data.error || 'خطایی رخ داد'}`);
      }
    } catch (err) {
      setIsError(true);
      setMessage('❌ Network Error (اتصال به سرور برقرار نشد)');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md bg-[#110e2d]/60 backdrop-blur-xl border border-cyan-500/30 p-8 rounded-3xl shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-purple-600"></div>
      
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-white mb-2 font-vazirmatn">
          {isLogin ? 'ورود به سیستم' : 'ایجاد حساب جدید'}
        </h2>
        <p className="text-sm text-gray-400 font-vazirmatn">
          {isLogin ? 'برای ادامه وارد شوید' : 'حساب کاربری جدید بسازید'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-cyan-300 mb-2 font-vazirmatn">نام کاربری</label>
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required
            className="w-full px-4 py-3 bg-black/40 border border-white/10 rounded-xl text-white focus:outline-none focus:border-cyan-500 transition-colors font-vazirmatn"
            placeholder="نام کاربری خود را وارد کنید" />
        </div>
        <div>
          <label className="block text-sm font-medium text-cyan-300 mb-2 font-vazirmatn">رمز عبور</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
            className="w-full px-4 py-3 bg-black/40 border border-white/10 rounded-xl text-white focus:outline-none focus:border-cyan-500 transition-colors font-vazirmatn"
            placeholder="••••••••" />
        </div>

        <button type="submit" disabled={isLoading}
          className={`w-full py-3 rounded-xl font-bold text-white transition-all font-vazirmatn ${isLoading ? 'bg-gray-600 cursor-not-allowed' : 'bg-gradient-to-r from-cyan-500 to-purple-600 hover:shadow-lg hover:shadow-cyan-500/30'}`}>
          {isLoading ? 'در حال پردازش...' : (isLogin ? 'ورود' : 'ثبت‌نام')}
        </button>
      </form>

      {message && (
        <div className={`mt-4 p-3 rounded-xl text-sm text-center font-vazirmatn border ${isError ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-green-500/10 border-green-500/30 text-green-400'}`}>
          {message}
        </div>
      )}

      <div className="mt-6 text-center">
        <button onClick={() => { setIsLogin(!isLogin); setMessage(''); setIsError(false); }}
          className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors font-vazirmatn">
          {isLogin ? 'حساب ندارید؟ ثبت‌نام کنید' : 'حساب دارید؟ وارد شوید'}
        </button>
      </div>
    </div>
  );
}
