export default function Market({ onBack }: { onBack: () => void }) {
  return (
    <div className="z-10 w-full max-w-2xl px-4 pt-10 flex flex-col items-center">
      <div className="w-full bg-[#110e2d]/60 backdrop-blur-xl border border-green-500/30 p-8 rounded-2xl shadow-[0_0_30px_rgba(34,197,94,0.15)]">
        <div className="flex justify-between items-center mb-6">
          <button onClick={onBack} className="text-green-400 text-sm hover:underline font-vazirmatn">← بازگشت</button>
          <h2 className="text-2xl font-bold text-white font-vazirmatn">تحلیل بازار زنده</h2>
        </div>
        <div className="bg-black/40 border border-green-500/20 rounded-xl p-6 min-h-[200px] flex flex-col justify-center items-center">
          <p className="text-center text-green-400 font-vazirmatn">سرور تحلیل بازار در حال راه‌اندازی است...</p>
        </div>
      </div>
    </div>
  );
}
