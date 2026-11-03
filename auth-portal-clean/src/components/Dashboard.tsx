export default function Dashboard({ username, onLogout, onNavigate }: { username: string, onLogout: () => void, onNavigate: (page: string) => void }) {
  return (
    <div className="z-10 w-full max-w-5xl px-4 pt-10 flex flex-col items-center">
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
        {/* کارت پلتفرم Elen-d */}
        <a href="https://elen-seven.vercel.app" target="_blank" rel="noopener noreferrer" className="bg-[#110e2d]/60 backdrop-blur-xl border border-white/10 p-6 rounded-2xl hover:border-cyan-400/80 transition-all cursor-pointer group block text-right">
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">🛠️</div>
          <h3 className="text-lg font-bold text-white font-vazirmatn mb-2 flex items-center justify-between">
            پلتفرم Elen-d
            <span className="text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-1 rounded-md border border-cyan-500/30">آنلاین</span>
          </h3>
          <p className="text-xs text-gray-400 font-vazirmatn">مدیریت هوشمند تعمیرات و تحلیل بردهای الکترونیک.</p>
        </a>

        {/* کارت موتور محاسباتی */}
        <div onClick={() => onNavigate('mathbot')} className="bg-[#110e2d]/60 backdrop-blur-xl border border-white/10 p-6 rounded-2xl hover:border-cyan-400/50 transition-all cursor-pointer group">
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">🧮</div>
          <h3 className="text-lg font-bold text-white font-vazirmatn mb-2">موتور محاسباتی</h3>
          <p className="text-xs text-gray-400 font-vazirmatn">Mathbot و پردازش‌های فیزیکی.</p>
        </div>

        {/* کارت سنسور امنیتی */}
        <div onClick={() => onNavigate('security')} className="bg-[#110e2d]/60 backdrop-blur-xl border border-white/10 p-6 rounded-2xl hover:border-purple-400/50 transition-all cursor-pointer group">
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">🛡️</div>
          <h3 className="text-lg font-bold text-white font-vazirmatn mb-2">سنسور امنیتی</h3>
          <p className="text-xs text-gray-400 font-vazirmatn">پایش حملات Honeypot.</p>
        </div>

        {/* کارت تحلیل بازار */}
        <div onClick={() => onNavigate('market')} className="bg-[#110e2d]/60 backdrop-blur-xl border border-white/10 p-6 rounded-2xl hover:border-green-400/50 transition-all cursor-pointer group">
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">📊</div>
          <h3 className="text-lg font-bold text-white font-vazirmatn mb-2">تحلیل بازار</h3>
          <p className="text-xs text-gray-400 font-vazirmatn">سیگنال‌های فارکس و کالا.</p>
        </div>

        {/* کارت جدید: آزمایشگاه داروسازی */}
        <div onClick={() => onNavigate('pharmlab')} className="bg-[#110e2d]/60 backdrop-blur-xl border border-white/10 p-6 rounded-2xl hover:border-emerald-400/50 transition-all cursor-pointer group">
          <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">🧪</div>
          <h3 className="text-lg font-bold text-white font-vazirmatn mb-2">آزمایشگاه داروسازی</h3>
          <p className="text-xs text-gray-400 font-vazirmatn">تحلیل فرمول‌ها و ترکیبات دارویی.</p>
        </div>
      </div>
    </div>
  );
}
