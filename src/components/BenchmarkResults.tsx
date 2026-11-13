import { useEffect, useState } from 'react';

interface TestResult {
  name: string;
  file: string;
  status: string;
  time_seconds: number;
  summary: string;
}

interface BenchmarkData {
  timestamp: string;
  total_time_seconds: number;
  tests: TestResult[];
}

export default function BenchmarkResults() {
  const [data, setData] = useState<BenchmarkData | null>(null);

  useEffect(() => {
    // خواندن فایل JSON از پوشه public
    fetch('/benchmark_results.json')
      .then(res => res.json())
      .then(d => setData(d))
      .catch(err => console.error("خطا در خواندن نتایج:", err));
  }, []);

  if (!data) return <div className="text-center text-gray-400 p-4 animate-pulse">در حال بارگذاری نتایج تست...</div>;

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-slate-900/50 rounded-2xl border border-slate-700 backdrop-blur-md mt-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500">
          🧪 نتایج بنچمارک Elen-k
        </h2>
        <span className="text-sm text-gray-400">زمان کل: {data.total_time_seconds} ثانیه</span>
      </div>

      <div className="space-y-4">
        {data.tests.map((test, idx) => (
          <div key={idx} className="flex flex-col p-4 bg-slate-800/80 rounded-xl border border-slate-600/50">
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center gap-3">
                <span className={`w-3 h-3 rounded-full ${test.status === 'SUCCESS' ? 'bg-green-500 shadow-[0_0_10px_#22c55e]' : 'bg-red-500'}`}></span>
                <h3 className="text-lg font-semibold text-white">{test.name}</h3>
              </div>
              <span className="text-xs text-gray-400 bg-slate-700 px-2 py-1 rounded-md">{test.time_seconds}s</span>
            </div>
            <p className="text-sm text-gray-300 font-mono bg-black/40 p-3 rounded-lg overflow-x-auto text-left" dir="ltr">
              {test.summary || "بدون خروجی"}
            </p>
          </div>
        ))}
      </div>
      <div className="mt-4 text-xs text-center text-gray-500">
        آخرین اجرا: {data.timestamp}
      </div>
    </div>
  );
}
