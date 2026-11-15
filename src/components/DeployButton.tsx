'use client';

import { useState } from 'react';
import { Rocket, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function DeployButton() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const triggerDeploy = async () => {
    setLoading(true);
    setStatus('idle');
    
    try {
      // درخواست به API ورسل که شما ساختید
      const response = await fetch('https://elen-k56.vercel.app/api/deploy', {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.success) {
        setStatus('success');
        setMessage('نسخه جدید با موفقیت در حال انتشار است!');
      } else {
        setStatus('error');
        setMessage(data.error || 'خطا در انتشار');
      }
    } catch (error: any) {
      setStatus('error');
      setMessage('خطای شبکه: ' + error.message);
    } finally {
      setLoading(false);
      // پاک کردن پیام بعد از ۵ ثانیه
      setTimeout(() => {
        setStatus('idle');
        setMessage('');
      }, 5000);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={triggerDeploy}
        disabled={loading}
        className="group flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-300 transition hover:bg-cyan-400/20 disabled:opacity-50"
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Rocket className="h-4 w-4 transition group-hover:-translate-y-1 group-hover:translate-x-1" />
        )}
        <span>{loading ? 'در حال انتشار...' : 'Deploy to Cloud'}</span>
      </button>

      {/* نوتیفیکیشن (Toast) */}
      <AnimatePresence>
        {status !== 'idle' && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className={`absolute top-full mt-2 end-0 z-50 flex items-center gap-2 whitespace-nowrap rounded-xl border p-3 text-xs backdrop-blur-md ${
              status === 'success' 
                ? 'border-emerald-400/50 bg-emerald-900/80 text-emerald-200' 
                : 'border-red-400/50 bg-red-900/80 text-red-200'
            }`}
          >
            {status === 'success' ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
            {message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
