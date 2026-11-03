import os, subprocess, json, urllib.request

print("🛠️ 1. بازنویسی کامل صفحه سنسور امنیتی با مدیریت دقیق خطاها...")
frontend_path = os.path.expanduser('~/Nazi/auth-portal/src/components/Security.tsx')

security_code = '''import { useState, useEffect } from 'react';

export default function Security({ onBack }: { onBack: () => void }) {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const API_URL = 'https://elen-auth-backend.onrender.com';

  const fetchLogs = async () => {
    setLoading(true);
    setError('');
    setLogs([]);
    const token = localStorage.getItem('elen_token');
    
    if (!token) {
        setError('⚠️ شما لاگین نیستید. لطفا به داشبورد بازگردید و مجددا لاگین کنید.');
        setLoading(false);
        return;
    }

    try {
      const res = await fetch(API_URL + '/api/security/logs', {
          headers: { 'Authorization': 'Bearer ' + token }
      });
      
      if (res.status === 503) {
          setError('🚨 سیستم به دلیل تهدید امنیتی (Lockdown) موقتا قفل شده است. لطفا ۳ دقیقه صبر کنید.');
          return;
      }
      if (res.status === 401) {
          setError('⚠️ توکن شما منقضی شده است. لطفا از حساب خارج شده و دوباره لاگین کنید.');
          return;
      }
      
      const data = await res.json();
      if (data.success) {
          setLogs(data.logs);
          if (data.logs.length === 0) setError('هیچ لاگی یافت نشد.');
      } else {
          setError(data.message || 'خطای نامشخص در سرور');
      }
    } catch (e) {
      setError('⚠️ خطای شبکه (سرور در حال بیدار شدن است. ۳۰ ثانیه صبر کنید و دوباره تلاش کنید)');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(); }, []);

  return (
    <div className="z-10 w-full max-w-2xl px-4 pt-10 flex flex-col items-center">
      <div className="w-full bg-[#110e2d]/60 backdrop-blur-xl border border-purple-500/30 p-8 rounded-2xl shadow-[0_0_30px_rgba(168,85,247,0.15)]">
        <div className="flex justify-between items-center mb-6">
          <button onClick={onBack} className="text-purple-400 text-sm hover:underline font-vazirmatn">← بازگشت به داشبورد</button>
          <h2 className="text-2xl font-bold text-white font-vazirmatn">سنسور امنیتی (Honeypot)</h2>
        </div>
        
        <p className="text-gray-400 text-sm text-right mb-6 font-vazirmatn">
          پایش زنده حملات به سرور آلمان. سیستم هانی‌پات هرگونه نفوذ را شناسایی و مسدود می‌کند.
        </p>

        <div className="bg-black/40 border border-purple-500/20 rounded-xl p-4 mb-6 min-h-[250px] flex flex-col justify-center">
          {loading ? (
             <div className="flex justify-center"><div className="w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div></div>
          ) : error ? (
             <div className="text-red-400 text-center text-sm bg-red-500/10 p-4 rounded-lg border border-red-500/30 font-vazirmatn">{error}</div>
          ) : logs.length > 0 ? (
            <div className="space-y-3">
              {logs.map((log, i) => (
                <div key={i} className="flex justify-between items-center text-sm p-3 bg-white/5 rounded-lg border border-white/5 font-mono">
                  <span className="text-gray-500">{log.time}</span>
                  <span className="text-red-400 font-bold">{log.type}</span>
                  <span className="text-gray-300">{log.ip}</span>
                  <span className="px-2 py-1 bg-red-500/20 text-red-300 rounded text-xs">{log.status}</span>
                </div>
              ))}
            </div>
          ) : null}
        </div>

        <button onClick={fetchLogs} disabled={loading} className="w-full bg-gradient-to-r from-purple-500 to-red-600 text-white font-bold py-3 rounded-lg hover:opacity-90 transition-all font-vazirmatn disabled:opacity-50">
          {loading ? 'در حال دریافت...' : 'به‌روزرسانی لاگ‌ها'}
        </button>
      </div>
    </div>
  );
}
'''

with open(frontend_path, 'w', encoding='utf-8') as f:
    f.write(security_code)

print("🚀 2. ارسال به Vercel...")
subprocess.run(["bash", "-c", "cd ~/Nazi/auth-portal && unset VERCEL_TOKEN && vercel --prod --yes --force > /dev/null 2>&1"])
print("✅ Vercel آپدیت شد.")

print("🚀 3. ارسال دستور بیلد مجدد به Render (برای اطمینان از نصب PyJWT)...")
render_key = open(os.path.expanduser('~/render_key.txt')).read().strip()
headers = {'Authorization': f'Bearer {render_key}', 'Accept': 'application/json'}
services = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.render.com/v1/services', headers=headers)).read().decode())
for s in services:
    if s['service']['name'] == 'elen-auth-backend':
        srv_id = s['service']['id']
        urllib.request.urlopen(urllib.request.Request(f'https://api.render.com/v1/services/{srv_id}/deploys', headers=headers, method='POST'))
        print("🏆 تمام شد! دستور بیلد Render صادر شد.")
        break
