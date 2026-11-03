#!/data/data/com.termux/files/usr/bin/bash
# ==========================================================
# 🎨 ELEN UI Restoration Module (Galaxy & Glassmorphism)
# ==========================================================

echo "🎨 ربات در حال بازگرداندن ظاهر چند میلیون دلاری..."

cd ~/Nazi/auth-portal || { echo "❌ پوشه پیدا نشد"; exit 1; }

# ۱. آماده‌سازی فونت وزیرمتن در index.html
echo "🔤 مرحله ۱: تنظیم فونت وزیرمتن..."
cat << 'HTML' > index.html
<!doctype html>
<html lang="fa" dir="rtl">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ELEN Secure Terminal</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
HTML

# ۲. ساخت پس‌زمینه کهکشانی (Starfield)
echo "🌌 مرحله ۲: ساخت پس‌زمینه کهکشانی و ستاره‌های متحرک..."
cat << 'TSX' > src/components/Starfield.tsx
import { useEffect, useRef } from 'react';

export default function Starfield() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const stars = Array.from({ length: 150 }).map(() => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 1.5,
      speed: Math.random() * 0.5 + 0.1,
    }));

    let animationFrameId: number;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#0B0A1A';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      stars.forEach((star) => {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fill();

        star.y -= star.speed;
        if (star.y < 0) {
          star.y = canvas.height;
          star.x = Math.random() * canvas.width;
        }
      });
      animationFrameId = requestAnimationFrame(render);
    };
    render();

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);
    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none" />;
}
TSX

# ۳. ساخت لوگوی هولوگرافیک ELEN
echo "🪐 مرحله ۳: ساخت لوگوی هولوگرافیک..."
cat << 'TSX' > src/components/Logo.tsx
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
TSX

# ۴. چیدمان نهایی (App)
echo "🎬 مرحله ۴: چیدمان نهایی صفحه..."
cat << 'TSX' > src/App.tsx
import Starfield from './components/Starfield';
import Logo from './components/Logo';
import AuthCard from './components/AuthCard';

export default function App() {
  return (
    <div className="relative min-h-screen bg-[#0B0A1A] overflow-hidden flex flex-col items-center justify-center font-vazirmatn">
      <Starfield />
      <div className="z-10 flex flex-col items-center w-full px-4 pt-10">
        <Logo />
        <AuthCard />
      </div>
    </div>
  );
}
TSX

# ۵. دیپلوی نهایی روی Vercel
echo "🚀 مرحله ۵: ارسال به Vercel برای آپدیت نهایی..."
unset VERCEL_TOKEN
vercel --prod --yes --force > deploy_ui.log 2>&1

if grep -q "Ready in" deploy_ui.log; then
    echo "🏆🏆🏆 پیروزی کامل! ظاهر افسانه‌ای با موفقیت بازگردانده شد."
    echo "🌐 آدرس سایت: https://auth-portal-ruby.vercel.app"
else
    echo "⚠️ ورسل آپدیت شد اما ممکن است نیاز به بررسی لاگ داشته باشد."
    tail -n 10 deploy_ui.log
fi
