import { useEffect, useState, type ReactNode } from "react";
import { AnimatePresence, motion, type Variants } from "framer-motion";
import { Brain, TerminalSquare, Server, Cpu, ShieldCheck, Activity } from "lucide-react";
import ChatPanel from "./workspace/ChatPanel";
import TerminalPanel from "./workspace/TerminalPanel";
import DeployPanel from "./workspace/DeployPanel";

function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(() => typeof window !== "undefined" ? window.matchMedia(query).matches : false);
  useEffect(() => {
    const mql = window.matchMedia(query);
    const onChange = () => setMatches(mql.matches);
    onChange();
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, [query]);
  return matches;
}

function useClock() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return now;
}

type TabId = "chat" | "terminal" | "deploy";
const TABS = [
  { id: "chat", label: "Elen-k", icon: <Brain size={20} />, color: "text-purple-300", glow: "shadow-[0_0_15px_rgba(168,85,247,0.6)] border-purple-400/60 bg-purple-500/15" },
  { id: "terminal", label: "Termux", icon: <TerminalSquare size={20} />, color: "text-cyan-300", glow: "shadow-[0_0_15px_rgba(34,211,238,0.6)] border-cyan-400/60 bg-cyan-500/15" },
  { id: "deploy", label: "Deploy-bot", icon: <Server size={20} />, color: "text-emerald-300", glow: "shadow-[0_0_15px_rgba(52,211,153,0.6)] border-emerald-400/60 bg-emerald-500/15" },
];

const PANELS = { chat: () => <ChatPanel />, terminal: () => <TerminalPanel />, deploy: () => <DeployPanel /> };
const slide = { enter: (dir: number) => ({ x: dir > 0 ? "-100%" : "100%", opacity: 0, scale: 0.96 }), center: { x: 0, opacity: 1, scale: 1 }, exit: (dir: number) => ({ x: dir > 0 ? "100%" : "-100%", opacity: 0, scale: 0.96 }) };

function Header() {
  const now = useClock();
  const title = "Elen-k Unified Workspace";
  return (
    <motion.header initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease: "easeOut" }} className="relative shrink-0 overflow-hidden rounded-2xl border border-white/10 bg-black/40 px-4 py-3 backdrop-blur-xl sm:px-6">
      <div className="holo-sweep" />
      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-cyan-400/70 to-transparent" />
      <div className="relative flex items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <div className="relative grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-cyan-400/40 bg-gradient-to-br from-cyan-500/20 to-purple-600/20 shadow-[0_0_15px_rgba(34,211,238,0.5)]">
            <img src="/logo.webp" alt="Elen-k" className="w-8 h-8 object-contain" />
            <span className="absolute -left-0.5 -top-0.5 h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
          </div>
          <div className="min-w-0">
            <h1 className="flex flex-wrap items-baseline gap-x-2 leading-tight">
              <span dir="ltr" data-text={title} className="holo-text holo-glitch font-mono text-base font-semibold tracking-tight sm:text-xl">{title}</span>
              <span className="hidden text-slate-500 sm:inline">|</span>
              <span className="text-xs font-bold text-slate-200 sm:text-base">سه همکار در یک پلتفرم</span>
            </h1>
          </div>
        </div>
        <div className="hidden items-center gap-2 md:flex" dir="ltr">
          <Chip icon={<ShieldCheck size={12} />} label="E2E SECURED" tone="emerald" />
          <Chip icon={<Activity size={12} />} label="3/3 AGENTS" tone="cyan" />
          <div className="rounded-lg border border-white/10 bg-white/5 px-2.5 py-1 font-mono text-[11px] text-slate-300">{now.toLocaleTimeString("en-GB", { hour12: false })}</div>
        </div>
      </div>
    </motion.header>
  );
}

function Chip({ icon, label, tone }: { icon: ReactNode; label: string; tone: "emerald" | "cyan" }) {
  const cls = tone === "emerald" ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-300" : "border-cyan-400/30 bg-cyan-400/10 text-cyan-300";
  return <span className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1 font-mono text-[10px] ${cls}`}>{icon}{label}</span>;
}

function BottomNav({ active, onChange }: { active: TabId; onChange: (id: TabId) => void }) {
  return (
    <nav className="relative shrink-0 rounded-2xl border border-white/10 bg-black/50 p-1.5 backdrop-blur-xl" style={{ marginBottom: "env(safe-area-inset-bottom)" }}>
      <ul className="grid grid-cols-3 gap-1">
        {TABS.map((tab) => {
          const isActive = tab.id === active;
          return (
            <li key={tab.id}>
              <button onClick={() => onChange(tab.id as TabId)} aria-current={isActive ? "page" : undefined} className={`relative flex w-full flex-col items-center gap-0.5 rounded-xl py-2 transition-colors ${isActive ? tab.color : "text-slate-500"}`}>
                {isActive && <motion.span layoutId="nav-pill" className={`absolute inset-0 rounded-xl border ${tab.glow}`} transition={{ type: "spring", stiffness: 420, damping: 32 }} />}
                <span className="relative">{tab.icon}</span>
                <span className="relative font-mono text-[10px] font-medium" dir="ltr">{tab.label}</span>
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export default function Workspace() {
  const isDesktop = useMediaQuery("(min-width: 1024px)");
  const [[active, direction], setTab] = useState<[TabId, number]>(["chat", 0]);

  const changeTab = (id: TabId) => {
    if (id === active) return;
    const from = TABS.findIndex((t) => t.id === active);
    const to = TABS.findIndex((t) => t.id === id);
    setTab([id, to > from ? 1 : -1]);
  };

  return (
    <div dir="rtl" className="relative flex h-[100dvh] flex-col gap-3 p-2.5 sm:p-4 lg:gap-4">
      <Header />
      {isDesktop ? (
        <main className="grid min-h-0 flex-1 grid-cols-[35fr_40fr_25fr] gap-4">
          {(["chat", "terminal", "deploy"] as TabId[]).map((id, i) => (
            <motion.div key={id} className="min-h-0" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + i * 0.12, duration: 0.6, ease: "easeOut" }}>
              {PANELS[id]()}
            </motion.div>
          ))}
        </main>
      ) : (
        <>
          <main className="relative min-h-0 flex-1 overflow-hidden">
            <AnimatePresence initial={false} custom={direction} mode="popLayout">
              <motion.div key={active} custom={direction} variants={slide} initial="enter" animate="center" exit="exit" transition={{ x: { type: "spring", stiffness: 320, damping: 34 }, opacity: { duration: 0.2 } }} className="absolute inset-0">
                {PANELS[active]()}
              </motion.div>
            </AnimatePresence>
          </main>
          <BottomNav active={active} onChange={changeTab} />
        </>
      )}
    </div>
  );
}
