export default function PharmLab({ onBack }: { onBack: () => void }) {
  return (
    <div className="z-10 w-full max-w-5xl px-4 pt-10 flex flex-col items-center">
      <div className="w-full flex justify-between items-center mb-8 bg-[#110e2d]/60 backdrop-blur-xl border border-emerald-500/30 p-4 rounded-2xl shadow-lg">
        <div className="flex items-center gap-4">
          <div className="text-4xl">🧪</div>
          <div>
            <h2 className="text-xl font-bold text-white font-vazirmatn">آزمایشگاه داروسازی</h2>
            <p className="text-sm text-emerald-400 font-vazirmatn">تحلیل و پردازش‌های تخصصی دارویی</p>
          </div>
        </div>
        <button onClick={onBack} className="px-4 py-2 bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 rounded-lg hover:bg-emerald-500/30 transition-colors text-sm font-vazirmatn">
          بازگشت
        </button>
      </div>
      
      <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#110e2d]/60 backdrop-blur-xl border border-white/10 p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-white font-vazirmatn mb-4">فرمول‌های ترکیبی</h3>
          <p className="text-sm text-gray-400 font-vazirmatn">در این بخش می‌توانید فرمول‌های شیمیایی و دوزهای دارویی را محاسبه و تحلیل کنید.</p>
        </div>
        <div className="bg-[#110e2d]/60 backdrop-blur-xl border border-white/10 p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-white font-vazirmatn mb-4">پایگاه داده داروها</h3>
          <p className="text-sm text-gray-400 font-vazirmatn">جستجو در میان ترکیبات، تداخلات دارویی و اطلاعات دارویی.</p>
        </div>
      </div>
    </div>
  );
}
