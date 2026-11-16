'use client';

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence, animate } from "framer-motion";
import {
  Globe, Activity, Dna, Upload, Play, Loader2, Cpu, Sigma, Copy, Check,
  BookOpen, Code2, FileText, ChevronDown, Sparkles, ArrowRight,
} from "lucide-react";

import DNAScene from "../components/DNAScene";
import DeployButton from "../components/DeployButton";
import { dict, type Lang, type Dict } from "@/lib/i18n";
import { checkHealth, discover, type Domain, type DiscoverResponse } from "@/lib/api";

const SAMPLE = `X0,X1,y
1.0,2.0,5.5
2.0,1.0,4.5
3.0,0.5,5.75
0.5,3.0,7.625
4.0,2.0,13.0`;

function Navbar({ t, lang, setLang, online }: { t: Dict; lang: Lang; setLang: (l: Lang) => void; online: boolean }) {
  return (
    <header className="fixed top-0 inset-x-0 z-50">
      <div className="mx-auto max-w-7xl px-4 mt-4">
        <nav className="glass rounded-2xl px-5 py-3 flex items-center justify-between">
          <a href="#" className="flex items-center gap-3">
            <div className="relative h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-400 to-emerald-400 grid place-items-center shadow-[0_0_20px_rgba(34,211,238,0.6)]">
              <Dna className="h-5 w-5 text-slate-950" />
            </div>
            <span className="font-bold tracking-tight text-white" dir="ltr">
              Elen-k <span className="text-cyan-300">Health OS</span>
            </span>
          </a>
          <div className="flex items-center gap-3">
            <DeployButton />
            <div className="hidden sm:flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-xs">
              <span className="relative flex h-2.5 w-2.5">
                <span className={`absolute inline-flex h-full w-full rounded-full ${online ? "bg-emerald-400" : "bg-amber-400"} opacity-75 animate-ping`} />
                <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${online ? "bg-emerald-400" : "bg-amber-400"}`} />
              </span>
              <span className={online ? "text-emerald-300" : "text-amber-300"}>{online ? t.online : t.offline}</span>
            </div>
            <button
              onClick={() => setLang(lang === "en" ? "fa" : "en")}
              className="flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/5 px-3 py-1.5 text-xs font-semibold hover:bg-cyan-400/15 transition"
            >
              <Globe className="h-4 w-4 text-cyan-300" />
              <span dir="ltr" className="font-sans">
                <span className={lang === "en" ? "text-cyan-300" : "text-slate-500"}>EN</span>
                <span className="mx-1 text-slate-600">|</span>
                <span className={lang === "fa" ? "text-cyan-300" : "text-slate-500"}>FA</span>
              </span>
            </button>
          </div>
        </nav>
      </div>
    </header>
  );
}

function Hero({ t }: { t: Dict }) {
  return (
    <section className="relative min-h-screen flex items-center pt-28 overflow-hidden">
      <div className="absolute inset-0 grid-bg" />
      <div className="absolute -top-40 start-1/4 h-[500px] w-[500px] rounded-full bg-cyan-500/20 blur-[120px]" />
      <div className="absolute bottom-0 end-0 h-[400px] w-[400px] rounded-full bg-emerald-500/15 blur-[120px]" />
      <div className="relative mx-auto max-w-7xl px-4 grid lg:grid-cols-2 gap-10 items-center w-full">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/5 px-3 py-1 text-xs text-cyan-200 mb-6">
            <Sparkles className="h-3.5 w-3.5" /> {t.badge}
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight text-white">
            {t.title1}{" "}
            <span className="bg-gradient-to-r from-cyan-300 via-teal-300 to-emerald-400 bg-clip-text text-transparent">{t.title2}</span>
          </h1>
          <p className="mt-5 text-lg text-teal-200 text-glow font-medium">{t.subtitle}</p>
          <p className="mt-4 max-w-xl text-slate-400 leading-relaxed">{t.desc}</p>
          <div className="mt-8 flex flex-wrap gap-4">
            <a href="#console" className="group relative inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-7 py-3.5 font-bold text-slate-950 shadow-[0_0_30px_rgba(45,212,191,0.6)] hover:shadow-[0_0_50px_rgba(45,212,191,0.9)] transition">
              {t.cta}
              <ArrowRight className="h-5 w-5 transition group-hover:translate-x-1 rtl:rotate-180 rtl:group-hover:-translate-x-1" />
            </a>
            <a href="#" className="inline-flex items-center gap-2 rounded-xl border border-slate-700 px-6 py-3.5 font-semibold text-slate-200 hover:border-cyan-400/50 transition">
              <BookOpen className="h-5 w-5" /> {t.docs}
            </a>
          </div>
          <div className="mt-12 grid grid-cols-3 gap-4 max-w-md">
            {t.stats.map(([v, l]) => (
              <div key={l} className="border-s-2 border-cyan-400/40 ps-3">
                <div className="text-2xl font-bold text-white">{v}</div>
                <div className="text-xs text-slate-500">{l}</div>
              </div>
            ))}
          </div>
        </motion.div>
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 1.2 }} className="relative h-[460px] lg:h-[620px]">
          <div className="absolute inset-10 rounded-full border border-cyan-400/10" />
          <div className="absolute inset-24 rounded-full border border-emerald-400/10" />
          <DNAScene />
        </motion.div>
      </div>
    </section>
  );
}

function R2Ring({ value }: { value: number }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const c = animate(0, value, { duration: 1.6, ease: "easeOut", onUpdate: setDisplay });
    return () => c.stop();
  }, [value]);
  const r = 54, C = 2 * Math.PI * r;
  return (
    <div className="relative h-36 w-36">
      <svg viewBox="0 0 128 128" className="h-full w-full -rotate-90">
        <defs>
          <linearGradient id="g" x1="0" x2="1">
            <stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#4ade80" />
          </linearGradient>
        </defs>
        <circle cx="64" cy="64" r={r} stroke="rgba(56,189,248,0.1)" strokeWidth="10" fill="none" />
        <circle cx="64" cy="64" r={r} stroke="url(#g)" strokeWidth="10" fill="none" strokeLinecap="round"
          strokeDasharray={C} strokeDashoffset={C * (1 - display)} style={{ filter: "drop-shadow(0 0 8px rgba(45,212,191,0.8))" }} />
      </svg>
      <div className="absolute inset-0 grid place-items-center" dir="ltr">
        <span className="text-2xl font-bold text-white font-mono">{display.toFixed(4)}</span>
      </div>
    </div>
  );
}

function Console({ t }: { t: Dict }) {
  const [domain, setDomain] = useState<Domain>("physics_all");
  const [data, setData] = useState("");
  const [fileName, setFileName] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DiscoverResponse | null>(null);
  const [copied, setCopied] = useState(false);
  const [drag, setDrag] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const readFile = (f: File) => {
    setFileName(f.name);
    f.text().then(setData);
  };

  const run = async () => {
    setLoading(true); setResult(null);
    const trimmed = data.trim();
    const res = await discover({ domain, data: trimmed, format: trimmed.startsWith("{") || trimmed.startsWith("[") ? "json" : "csv" });
    setResult(res); setLoading(false);
  };

  const copy = () => {
    if (!result) return;
    navigator.clipboard?.writeText(result.formula);
    setCopied(true); setTimeout(() => setCopied(false), 1500);
  };

  return (
    <section id="console" className="relative py-24">
      <div className="mx-auto max-w-7xl px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-white">{t.dashTitle}</h2>
          <p className="mt-3 text-slate-400">{t.dashSub}</p>
        </motion.div>
        <div className="grid lg:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} className="glass rounded-3xl p-6 flex flex-col gap-5">
            <div className="flex items-center justify-between">
              <h3 className="flex items-center gap-2 font-semibold text-white"><Upload className="h-5 w-5 text-cyan-300" />{t.input}</h3>
              <button onClick={() => { setData(SAMPLE); setFileName(null); }} className="text-xs text-cyan-300 hover:text-cyan-200">{t.sample}</button>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-slate-500">{t.domain}</label>
              <div className="relative mt-2">
                <select value={domain} onChange={(e) => setDomain(e.target.value as Domain)}
                  className="w-full appearance-none rounded-xl bg-slate-900/60 border border-cyan-400/20 px-4 py-3 pe-10 text-slate-100 focus:outline-none focus:border-cyan-400/60 focus:ring-2 focus:ring-cyan-400/20">
                  {(Object.keys(t.domains) as Domain[]).map((k) => <option key={k} value={k}>{t.domains[k]}</option>)}
                </select>
                <ChevronDown className="pointer-events-none absolute end-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              </div>
            </div>
            <textarea value={data} onChange={(e) => setData(e.target.value)} placeholder={t.placeholder} rows={8} dir="ltr"
              className="w-full resize-none rounded-xl bg-slate-950/60 border border-cyan-400/20 p-4 font-mono text-sm text-emerald-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-400/60 focus:ring-2 focus:ring-cyan-400/20" />
            <div
              onClick={() => fileRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
              onDragLeave={() => setDrag(false)}
              onDrop={(e) => { e.preventDefault(); setDrag(false); const f = e.dataTransfer.files[0]; if (f) readFile(f); }}
              className={`cursor-pointer rounded-xl border-2 border-dashed p-5 text-center text-sm transition ${drag ? "border-emerald-400 bg-emerald-400/10" : "border-cyan-400/20 hover:border-cyan-400/50"}`}>
              <FileText className="mx-auto mb-2 h-6 w-6 text-cyan-300" />
              <span className="text-slate-400">{fileName ? `${t.loaded}: ${fileName}` : t.drop}</span>
              <input ref={fileRef} type="file" accept=".json,.csv" hidden onChange={(e) => e.target.files?.[0] && readFile(e.target.files[0])} />
            </div>
            <button onClick={run} disabled={loading}
              className="relative overflow-hidden rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 py-3.5 font-bold text-slate-950 shadow-[0_0_25px_rgba(34,211,238,0.45)] hover:shadow-[0_0_40px_rgba(34,211,238,0.7)] disabled:opacity-80 transition flex items-center justify-center gap-2">
              {loading ? <><Loader2 className="h-5 w-5 animate-spin" />{t.loading}</> : <><Play className="h-5 w-5 rtl:rotate-180" />{t.run}</>}
            </button>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} className="glass rounded-3xl p-6 flex flex-col">
            <h3 className="flex items-center gap-2 font-semibold text-white mb-5"><Activity className="h-5 w-5 text-emerald-300" />{t.results}</h3>
            <AnimatePresence mode="wait">
              {loading ? (
                <motion.div key="l" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex-1 grid place-items-center">
                  <div className="text-center">
                    <div className="relative mx-auto h-24 w-24">
                      <div className="absolute inset-0 rounded-full border-2 border-cyan-400/20" />
                      <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-cyan-400 animate-spin" />
                      <Cpu className="absolute inset-0 m-auto h-8 w-8 text-cyan-300 animate-pulse" />
                    </div>
                    <p className="mt-5 text-cyan-200">{t.loading}</p>
                  </div>
                </motion.div>
              ) : result ? (
                <motion.div key="r" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="flex flex-col gap-5">
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div className="rounded-2xl bg-slate-900/50 border border-cyan-400/10 p-5">
                      <div className="text-xs uppercase tracking-wider text-slate-500">{t.engine}</div>
                      <div className="mt-2 flex items-center gap-2 text-xl font-bold text-cyan-300 font-mono" dir="ltr"><Cpu className="h-5 w-5" />{result.engine}</div>
                    </div>
                    <div className="rounded-2xl bg-slate-900/50 border border-emerald-400/10 p-5 flex flex-col items-center">
                      <div className="text-xs uppercase tracking-wider text-slate-500 self-start">{t.r2}</div>
                      <R2Ring value={result.r2_score} />
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="flex items-center gap-2 text-xs uppercase tracking-wider text-slate-500"><Sigma className="h-4 w-4" />{t.formula}</span>
                      <button onClick={copy} className="flex items-center gap-1 text-xs text-cyan-300 hover:text-cyan-200">
                        {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}{copied ? t.copied : t.copy}
                      </button>
                    </div>
                    <pre dir="ltr" className="rounded-xl bg-slate-950/80 border border-emerald-400/30 p-5 font-mono text-base sm:text-lg text-emerald-300 overflow-x-auto">
                      <code>{result.formula}</code>
                    </pre>
                  </div>
                </motion.div>
              ) : (
                <motion.div key="e" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex-1 grid place-items-center text-center py-16">
                  <div>
                    <Code2 className="mx-auto h-12 w-12 text-slate-700" />
                    <p className="mt-4 max-w-xs text-slate-500">{t.awaiting}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

function Footer({ t }: { t: Dict }) {
  const icons = [BookOpen, Code2, FileText];
  return (
    <footer className="border-t border-cyan-400/10 py-10">
      <div className="mx-auto max-w-7xl px-4 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2 text-sm text-slate-500"><Dna className="h-4 w-4 text-cyan-400" />{t.footer}</div>
        <div className="flex items-center gap-6 text-sm">
          {t.links.map((l, i) => {
            const I = icons[i];
            return <a key={l} href="#" className="flex items-center gap-1.5 text-slate-400 hover:text-cyan-300 transition"><I className="h-4 w-4" />{l}</a>;
          })}
        </div>
      </div>
    </footer>
  );
}

export default function Home() {
  const [lang, setLang] = useState<Lang>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem("lang") as Lang) || "en";
    }
    return "en";
  });
  const [online, setOnline] = useState(true);
  const t = dict[lang];

  useEffect(() => {
    document.documentElement.dir = lang === "fa" ? "rtl" : "ltr";
    document.documentElement.lang = lang;
    if (typeof window !== 'undefined') {
      localStorage.setItem("lang", lang);
    }
  }, [lang]);

  useEffect(() => {
    checkHealth().then(setOnline);
    const id = setInterval(() => checkHealth().then(setOnline), 15000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className={`min-h-screen overflow-x-hidden ${lang === "fa" ? "font-fa" : "font-sans"}`}>
      <Navbar t={t} lang={lang} setLang={setLang} online={online} />
      <Hero t={t} />
      <Console t={t} />
      <Footer t={t} />
    </div>
  );
}
