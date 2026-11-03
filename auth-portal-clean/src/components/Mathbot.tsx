import { useState } from 'react';

export default function Mathbot({ onBack }: { onBack: () => void }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const runDiscovery = async () => {
    setLoading(true);
    setResult(null);
    setErrorMsg('');
    
    const token = localStorage.getItem('token'); // اصلاح نام توکن
    
    try {
      const res = await fetch('/api/proxy/api/math/discover', { // استفاده از پروکسی
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + token
        }
      });
      
      if (res.status === 503) { setErrorMsg('🚨 سیستم به دلیل تهدید امنیتی موقتا قفل شده است.'); return; }
      if (res.status === 401) { setErrorMsg('⚠️ دسترسی غیرمجاز. لطفا دوباره لاگین کنید.'); return; }
      if (!res.ok) throw new Error(`Server returned ${res.status}`);

      const data = await res.json();
      if (data.success) {
        setResult(data.result);
      } else {
        setErrorMsg('سرور پاسخ ناموفق داد.');
      }
    } catch (e: any) {
      setErrorMsg(`⚠️ خطا در ارتباط: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="z-10 w-full max-w-2xl px-4 pt-10 flex flex-col items-center">
      <div className="w-full bg-[#110e2d]/60 backdrop-blur-xl border border-cyan-500/30 p-8 rounded-2xl shadow-[0_0_30px_rgba(6,182,212,0.15)]">
        <div className="flex justify-between items-center mb-6">
          <button onClick={onBack} className="text-cyan-400 text-sm hover:underline font-vazirmatn">← بازگشت به داشبورد</button>
          <h2 className="text-2xl font-bold text-white font-vazirmatn">موتور کشف ریاضی</h2>
        </div>
        
        <p className="text-gray-400 text-sm text-right mb-6 font-vazirmatn">
          این بخش به موتور Mathbot متصل است. با کلیک روی دکمه زیر، الگوریتم‌های کشف روی داده‌های علمی اجرا می‌شوند.
        </p>

        <div className="flex flex-col items-center justify-center min-h-[200px] border border-dashed border-cyan-500/30 rounded-xl bg-black/20 p-6 mb-6">
          {loading ? (
            <div className="flex flex-col items-center">
              <div className="w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-cyan-400 animate-pulse font-vazirmatn text-center">در حال پردازش بردارها در سرور...<br/><span className="text-xs text-gray-500">(ممکن است بار اول ۳۰ تا ۵۰ ثانیه طول بکشد)</span></p>
            </div>
          ) : errorMsg ? (
            <div className="text-center text-red-400 text-sm font-vazirmatn bg-red-500/10 p-4 rounded-lg border border-red-500/30">
              {errorMsg}
            </div>
          ) : result ? (
            <div className="text-center w-full">
              <p className="text-green-400 text-sm mb-2 font-vazirmatn">✅ کشف موفقیت‌آمیز بود!</p>
              <div className="bg-black/50 p-4 rounded-lg border border-white/10 mb-2">
                <p className="text-xl text-white font-mono mb-2">{result.formula}</p>
                <p className="text-sm text-gray-400 font-vazirmatn">نوع الگو: {result.type}</p>
                <p className="text-sm text-gray-400 font-vazirmatn">دقت (R²): {result.r2}</p>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 font-vazirmatn">آماده برای اجرای الگوریتم...</p>
          )}
        </div>

        <button 
          onClick={runDiscovery} 
          disabled={loading}
          className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold py-3 rounded-lg hover:opacity-90 transition-all font-vazirmatn disabled:opacity-50"
        >
          {loading ? 'در حال محاسبه...' : 'اجرای کشف (Run Discovery)'}
        </button>
      </div>
    </div>
  );
}
