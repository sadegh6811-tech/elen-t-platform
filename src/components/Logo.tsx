export default function Logo() {
  return (
    <div className="z-10 flex flex-col items-center mb-8 relative">
      <h1 className="text-6xl font-bold text-white tracking-widest font-vazirmatn relative" style={{ textShadow: '0 0 20px rgba(0, 255, 255, 0.5)' }}>
        ELEN
        <span className="absolute -right-10 top-0 text-cyan-400 text-3xl animate-pulse">🪐</span>
      </h1>
      <div className="flex items-center gap-4 mt-2 text-gray-400 text-sm font-vazirmatn">
        <span className="w-16 h-px bg-cyan-500/50"></span>
        <span>محاسبات مداری · تاسیس ۲۰۲۶</span>
        <span className="w-16 h-px bg-cyan-500/50"></span>
      </div>
    </div>
  );
}
