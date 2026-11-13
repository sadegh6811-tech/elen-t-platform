import { useCallback, useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Server, Database, Cloud, Triangle, Loader2 } from "lucide-react";
import GlassPanel from "./GlassPanel";

type ServiceKey = "render" | "vercel" | "neon";
type ServiceState = "up" | "down" | "deploying";
interface Service { key: ServiceKey; name: string; role: string; icon: React.ReactNode; latency: number; }

const SERVICES: Service[] = [
  { key: "render", name: "Render", role: "Backend · بک‌اند", icon: <Cloud size={16} />, latency: 84 },
  { key: "vercel", name: "Vercel", role: "Frontend · فرانت‌اند", icon: <Triangle size={14} />, latency: 31 },
  { key: "neon", name: "Neon", role: "Database · پایگاه داده", icon: <Database size={16} />, latency: 112 },
];

type LogLevel = "INFO" | "SUCCESS" | "WARN" | "ERROR";
interface LogLine { id: number; time: string; level: LogLevel; msg: string; }
const levelColor: Record<LogLevel, string> = { INFO: "text-cyan-300", SUCCESS: "text-emerald-400", WARN: "text-amber-300", ERROR: "text-rose-400" };
const now = () => new Date().toLocaleTimeString("en-GB", { hour12: false });
let logId = 0;
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

interface Action { id: string; label: string; emoji: string; color: string; steps: [LogLevel, string, number][]; target?: ServiceKey; heal?: boolean; }

const ACTIONS: Action[] = [
  { id: "render", emoji: "🚀", label: "Deploy to Render", color: "cyan", target: "render", steps: [["INFO", "Triggering Render deploy hook...", 500], ["INFO", "Building Docker image (python:3.12-slim)...", 900], ["INFO", "Installing requirements.txt (42 packages)", 800], ["INFO", "Health check → GET /api/health", 600], ["SUCCESS", "Render build complete. Live on elen-k-api.onrender.com", 0]] },
  { id: "vercel", emoji: "▲", label: "Deploy to Vercel", color: "purple", target: "vercel", steps: [["INFO", "vercel --prod  (scope: elen-k)", 500], ["INFO", "Running vite build...", 900], ["INFO", "Uploading 38 static assets to Edge Network", 700], ["SUCCESS", "Vercel deployment ready → elen-k.vercel.app", 0]] },
  { id: "heal", emoji: "⚙️", label: "Auto-Heal", color: "green", heal: true, steps: [["INFO", "Scanning service mesh for anomalies...", 700], ["WARN", "Neon: connection pool exhausted (max=20)", 700], ["INFO", "Restarting pooler & rotating credentials...", 900], ["SUCCESS", "All systems nominal. Self-heal finished.", 0]] },
  { id: "github", emoji: "📦", label: "Push to GitHub", color: "slate", steps: [["INFO", "git add -A && git commit -m \"feat: elen-t benchmark v2\"", 500], ["INFO", "Pushing to origin/main...", 800], ["SUCCESS", "Pushed 7 commits → github.com/elen-k/core", 0]] },
];

const buttonStyles: Record<string, string> = {
  cyan: "border-cyan-400/50 text-cyan-200 hover:shadow-[0_0_15px_rgba(34,211,238,0.5)] hover:bg-cyan-400/10",
  purple: "border-purple-400/50 text-purple-200 hover:shadow-[0_0_15px_rgba(168,85,247,0.5)] hover:bg-purple-400/10",
  green: "border-emerald-400/50 text-emerald-200 hover:shadow-[0_0_15px_rgba(52,211,153,0.5)] hover:bg-emerald-400/10",
  slate: "border-slate-300/40 text-slate-200 hover:shadow-[0_0_15px_rgba(226,232,240,0.35)] hover:bg-white/10",
};

export default function DeployPanel() {
  const [status, setStatus] = useState<Record<ServiceKey, ServiceState>>({ render: "up", vercel: "up", neon: "down" });
  const [busy, setBusy] = useState<string | null>(null);
  const [logs, setLogs] = useState<LogLine[]>(() => [
    { id: logId++, time: now(), level: "INFO", msg: "Deploy-bot online. Watching 3 services." },
    { id: logId++, time: now(), level: "SUCCESS", msg: "Render: healthy (84ms)" },
    { id: logId++, time: now(), level: "SUCCESS", msg: "Vercel: healthy (31ms)" },
    { id: logId++, time: now(), level: "ERROR", msg: "Neon: health check timeout (5000ms)" },
  ]);
  const logRef = useRef<HTMLDivElement>(null);

  const push = useCallback((level: LogLevel, msg: string) => setLogs((l) => [...l.slice(-80), { id: logId++, time: now(), level, msg }]), []);
  useEffect(() => { const el = logRef.current; if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" }); }, [logs]);

  useEffect(() => {
    const beats = ["Heartbeat: render ✓ vercel ✓", "CDN cache hit ratio 97.4%", "Cron: backup snapshot queued", "Metrics flushed to observability sink"];
    const id = setInterval(() => { if (!document.hidden) push("INFO", beats[Math.floor(Math.random() * beats.length)]); }, 7000);
    return () => clearInterval(id);
  }, [push]);

  const run = async (action: Action) => {
    if (busy) return;
    setBusy(action.id);
    if (action.target) setStatus((s) => ({ ...s, [action.target!]: "deploying" }));
    if (action.heal) setStatus((s) => ({ ...s, neon: s.neon === "down" ? "deploying" : s.neon }));
    for (const [level, msg, delay] of action.steps) {
      push(level, msg);
      if (delay) await sleep(delay);
    }
    if (action.target) setStatus((s) => ({ ...s, [action.target!]: "up" }));
    if (action.heal) setStatus({ render: "up", vercel: "up", neon: "up" });
    setBusy(null);
  };

  const allUp = Object.values(status).every((s) => s === "up");

  return (
    <GlassPanel accent="green" title="Deploy-bot Status" subtitle="مدیر عملیات · DevOps Control Center" icon={<Server size={18} />} badge={
      <div className="flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-2.5 py-1">
        <span className="relative flex h-2.5 w-2.5"><span className="pulse-ring absolute inset-0 rounded-full bg-emerald-400" /><span className="relative h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399]" /></span>
        <span className="text-[10px] font-semibold text-emerald-300">ONLINE</span>
      </div>
    }>
      <div className="neon-scroll flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto p-4">
        <div>
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-xs font-semibold text-slate-300">وضعیت سرویس‌ها</h3>
            <span className={`text-[10px] font-mono ${allUp ? "text-emerald-400" : "text-rose-400"}`}>{allUp ? "ALL SYSTEMS GO" : "DEGRADED"}</span>
          </div>
          <ul className="space-y-2">
            {SERVICES.map((s) => {
              const st = status[s.key];
              return (
                <li key={s.key} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2.5">
                  <div className="flex items-center gap-3">
                    <span className="grid h-8 w-8 place-items-center rounded-lg bg-white/5 text-slate-200">{s.icon}</span>
                    <div><div className="text-sm font-semibold text-white" dir="ltr">{s.name}</div><div className="text-[10px] text-slate-400">{s.role}</div></div>
                  </div>
                  <div className="flex items-center gap-2" dir="ltr">
                    <span className="font-mono text-[10px] text-slate-500">{st === "up" ? `${s.latency}ms` : st === "deploying" ? "..." : "—"}</span>
                    {st === "deploying" ? <Loader2 size={12} className="animate-spin text-amber-300" /> : <span className={`h-2.5 w-2.5 rounded-full ${st === "up" ? "bg-emerald-400 shadow-[0_0_10px_#34d399]" : "animate-pulse bg-rose-500 shadow-[0_0_10px_#f43f5e]"}`} />}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
        <div>
          <h3 className="mb-2 text-xs font-semibold text-slate-300">عملیات سریع</h3>
          <div className="grid grid-cols-2 gap-2">
            {ACTIONS.map((a) => (
              <motion.button key={a.id} whileTap={{ scale: 0.96 }} disabled={!!busy} onClick={() => run(a)} dir="ltr" className={`relative flex items-center justify-center gap-1.5 overflow-hidden rounded-xl border bg-black/30 px-2 py-2.5 text-[11px] font-semibold transition-all disabled:cursor-not-allowed disabled:opacity-50 ${buttonStyles[a.color]}`}>
                {busy === a.id ? <Loader2 size={13} className="animate-spin" /> : <span>{a.emoji}</span>}<span className="truncate">{a.label}</span>
              </motion.button>
            ))}
          </div>
        </div>
        <div className="flex min-h-[160px] flex-1 flex-col">
          <div className="mb-2 flex items-center justify-between"><h3 className="text-xs font-semibold text-slate-300">لاگ استقرار</h3><span className="font-mono text-[10px] text-slate-500">{logs.length} lines</span></div>
          <div ref={logRef} dir="ltr" className="neon-scroll scanlines min-h-0 flex-1 overflow-y-auto rounded-xl border border-white/10 bg-black/60 p-3 font-mono text-[10.5px] leading-relaxed">
            {logs.map((l) => (
              <motion.div key={l.id} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} className="whitespace-pre-wrap break-words">
                <span className="text-slate-600">{l.time} </span><span className={levelColor[l.level]}>[{l.level}]</span> <span className="text-slate-300">{l.msg}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}
