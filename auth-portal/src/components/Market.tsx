import { useState, useEffect } from 'react';

export default function Market({ onBack }: { onBack: () => void }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const API_URL = 'https://elen-auth-backend.onrender.com';

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch(API_URL + '/api/market/analysis', {
      ...( {
      ...( {
      ...( {
      ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    } || {} ),
      headers: { ...( {
      ...(  || {} ),
      headers: { ...( ?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    }?.headers || {} ), 'Authorization': 'Bearer ' + localStorage.getItem('elen_token') }
    });
      const json = await res.json();
      if (json.success) setData(json.data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  return (
    <div className="z-10 w-full max-w-2xl px-4 pt-10 flex flex-col items-center">
      <div className="w-full bg-[#110e2d]/60 backdrop-blur-xl border border-green-500/30 p-8 rounded-2xl shadow-[0_0_30px_rgba(34,197,94,0.15)]">
        <div className="flex justify-between items-center mb-6">
          <button onClick={onBack} className="text-green-400 text-sm hover:underline font-vazirmatn">← بازگشت به داشبورد</button>
          <h2 className="text-2xl font-bold text-white font-vazirmatn">تحلیل بازار زنده</h2>
        </div>
        
        <p className="text-gray-400 text-sm text-right mb-6 font-vazirmatn">
          تحلیل لحظه‌ای بازار فارکس و فلزات گران‌بها با استفاده از الگوریتم‌های ELEN.
        </p>

        <div className="bg-black/40 border border-green-500/20 rounded-xl p-6 mb-6 min-h-[250px] flex flex-col justify-center">
          {loading ? (
             <div className="flex justify-center"><div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin"></div></div>
          ) : data ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center border-b border-white/10 pb-4">
                <span className="text-2xl font-mono text-white">{data.pair}</span>
                <span className="text-2xl font-bold text-green-400">{data.price}</span>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-2">
                 <div className="bg-white/5 p-3 rounded-lg border border-white/5">
                    <span className="block text-xs text-gray-500 mb-1">روند بازار</span>
                    <span className={`font-bold ${data.trend === 'Bullish' ? 'text-green-400' : 'text-red-400'}`}>{data.trend}</span>
                 </div>
                 <div className="bg-white/5 p-3 rounded-lg border border-white/5">
                    <span className="block text-xs text-gray-500 mb-1">اعتماد الگوریتم</span>
                    <span className="font-bold text-cyan-400">{data.confidence}%</span>
                 </div>
                 <div className="col-span-2 bg-white/5 p-3 rounded-lg border border-white/5">
                    <span className="block text-xs text-gray-500 mb-1">پیشنهاد سیستم</span>
                    <span className="font-bold text-white">{data.recommendation}</span>
                 </div>
              </div>
            </div>
          ) : (
            <p className="text-center text-gray-500 font-vazirmatn">داده‌ای موجود نیست.</p>
          )}
        </div>

        <button onClick={fetchData} disabled={loading} className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold py-3 rounded-lg hover:opacity-90 transition-all font-vazirmatn disabled:opacity-50">
          {loading ? 'در حال دریافت...' : 'به‌روزرسانی تحلیل'}
        </button>
      </div>
    </div>
  );
}
