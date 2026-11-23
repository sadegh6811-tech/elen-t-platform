"use client";

import { useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import Logo from "@/components/Logo";
import type { AvatarState } from "@/components/Avatar3D";
import {
  Brain, ChevronDown, Cpu, Database, History, Lock, Menu,
  MessagesSquare, Paperclip, Plus, Send, Server, Sparkles, Zap, Copy, Check,
} from "lucide-react";

const Avatar3D = dynamic(() => import("@/components/Avatar3D"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center">
      <div className="h-24 w-24 animate-pulse rounded-full bg-mint-500/20 blur-sm" />
    </div>
  ),
});

type ChatItem = { id: string; title: string; time: string; group: string; messages: number; };
const HISTORY: ChatItem[] = [
  { id: "1", title: "راهنمای اجرای vLLM", time: "۱۲:۴۳", group: "امروز", messages: 8 },
  { id: "2", title: "تنظیم nginx جلوی API", time: "۱۰:۵۷", group: "امروز", messages: 6 },
  { id: "3", title: "طراحی Custom Engine", time: "۱۷:۲۱", group: "دیروز", messages: 14 },
];
const GROUPS = ["امروز", "دیروز"];

type QuickPrompt = { label: string; message: string };
const QUICK_PROMPTS: QuickPrompt[] = [
  { label: "آیا داده‌ها بیرون از شبکه می‌روند؟", message: "آیا داده‌ها بیرون از شبکهٔ محلی می‌روند؟" },
  { label: "یک فرمول فیزیک به من بده", message: "یک فرمول فیزیک به من بده" },
  { label: "پروتکل پیش‌بینی را توضیح بده", message: "پروتکل پیش‌بینی Custom Engine چطور کار می‌کند؟" },
];

type ChatMessage = { id: string; role: "user" | "assistant"; content: string; time: string };

function nowTime() {
  return new Intl.DateTimeFormat("fa-IR", { hour: "2-digit", minute: "2-digit" }).format(new Date());
}

export default function HomePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [activeChat, setActiveChat] = useState("1");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pending]);

  // اتصال واقعی به بک‌اند (API)
  async function send(text: string) {
    const content = text.trim();
    if (!content || pending) return;

    const newMessages = [...messages, { id: crypto.randomUUID(), role: "user", content, time: nowTime() } as ChatMessage];
    setMessages(newMessages);
    setInput("");
    setPending(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          messages: newMessages.map(m => ({ role: m.role, content: m.content })) 
        }),
      });

      if (!res.ok) throw new Error("خطا در دریافت پاسخ");

      const data = await res.json();
      
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: data.message.content, time: nowTime() },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: "متأسفم، در حال حاضر ارتباط با سرور برقرار نیست.", time: nowTime() },
      ]);
    } finally {
      setPending(false);
    }
  }

  function newChat() {
    setMessages([]);
    setInput("");
    setPending(false);
    setSidebarOpen(false);
    setActiveChat("new");
  }

  const hasMessages = messages.length > 0;
  const avatarState: AvatarState = pending ? "thinking" : hasMessages ? "responding" : "idle";

  return (
    <div className="flex h-dvh overflow-hidden">
      <aside
        className={`fixed inset-y-0 right-0 z-40 flex w-[300px] flex-col border-e border-white/8 bg-night-900/95 px-5 py-6 backdrop-blur-xl transition-transform duration-300 ease-out lg:static lg:z-auto lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0 shadow-card" : "translate-x-full"
        }`}
      >
        <div className="flex items-center gap-3">
          <Logo size={44} className="shrink-0 drop-shadow-[0_0_14px_rgba(0,229,255,0.45)]" />
          <div>
            <p className="text-lg font-extrabold leading-tight text-slate-100">هستی</p>
            <p className="text-[11px] text-slate-500">دستیار هوش‌مصنوعی خصوصی</p>
          </div>
        </div>

        <button onClick={newChat} className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-mint-400 px-4 py-2.5 text-sm font-bold text-night-950 hover:bg-mint-300 active:scale-[0.98]">
          <Plus size={18} strokeWidth={2.6} /> گفتگوی جدید
        </button>

        <div className="mt-6 mb-3 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-widest text-slate-500">
          <History size={13} /> تاریخچه
        </div>

        <nav className="scroll-area flex-1 space-y-5 overflow-y-auto pe-1">
          {GROUPS.map((group) => {
            const items = HISTORY.filter((c) => c.group === group);
            if (items.length === 0) return null;
            return (
              <div key={group}>
                <p className="mb-2 text-[11px] font-medium text-slate-500">{group}</p>
                <ul className="space-y-1">
                  {items.map((item) => {
                    const isActive = activeChat === item.id;
                    return (
                      <li key={item.id}>
                        <button onClick={() => setActiveChat(item.id)} className={`group flex w-full items-start gap-3 rounded-xl border-s-2 px-3 py-2.5 text-right transition ${isActive ? "border-mint-400/80 bg-mint-500/10 text-slate-100" : "border-transparent text-slate-400 hover:bg-white/5 hover:text-slate-200"}`}>
                          <MessagesSquare size={16} className={`mt-0.5 shrink-0 transition ${isActive ? "text-mint-300" : "text-slate-600 group-hover:text-slate-400"}`} />
                          <span className="min-w-0 flex-1">
                            <span className="block truncate text-[13px] font-medium">{item.title}</span>
                          </span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
        </nav>

        <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.03] p-3.5">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-slate-300">
              <Brain size={16} className="text-mint-300" /><span className="text-xs font-semibold">مدل فعلی</span>
            </div>
            <span className="inline-flex items-center gap-1 rounded-full bg-mint-500/15 px-2 py-0.5 text-[10px] font-bold text-mint-300">
              <span className="relative flex h-1.5 w-1.5"><span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-mint-400 opacity-75" /><span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-mint-400" /></span>
              آماده
            </span>
          </div>
          <p dir="ltr" className="mt-2 truncate text-[12px] font-medium text-slate-200">Qwen3-Coder-30B-A3B-AWQ</p>
        </div>
      </aside>

      {sidebarOpen && <button className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden" onClick={() => setSidebarOpen(false)} />}

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-3 border-b border-white/8 bg-night-900/60 px-4 py-3 backdrop-blur-xl sm:px-6">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen((v) => !v)} className="grid h-10 w-10 place-items-center rounded-xl border border-white/10 bg-white/5 text-slate-300 transition hover:bg-white/10 lg:hidden">
              <Menu size={19} />
            </button>
            <button className="flex items-center gap-2.5 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm transition hover:bg-white/10">
              <Brain size={17} className="shrink-0 text-glow-400" />
              <span className="hidden text-[13px] font-medium text-slate-200 sm:block" dir="ltr">Qwen3-Coder-30B-A3B-AWQ</span>
              <ChevronDown size={15} className="shrink-0 text-slate-500" />
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button onClick={() => { navigator.clipboard.writeText(window.location.href); alert("لینک کپی شد!"); }} className="flex items-center justify-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-[11px] font-semibold text-slate-300 transition hover:bg-white/10 hover:text-white" dir="rtl">
              <Copy size={14} /><span className="hidden sm:inline">کپی لینک</span>
            </button>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1.5 text-[11px] font-semibold text-slate-300" dir="ltr">
              <span className="relative flex h-1.5 w-1.5"><span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-mint-400 opacity-75" /><span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-mint-400" /></span>
              <Server size={13} /> vllm · 8000
            </span>
            <div className="ms-2 grid h-10 w-10 place-items-center rounded-full bg-gradient-to-br from-mint-400 to-glow-500 shadow-glow ring-2 ring-white/10">
              <Zap size={17} className="text-night-950" strokeWidth={2.6} />
            </div>
          </div>
        </header>

        <div className="scroll-area relative flex-1 overflow-y-auto">
          {!hasMessages ? (
            <div className="flex min-h-full flex-col items-center justify-center px-6 py-10 text-center">
              <div className="relative h-[38vh] min-h-[280px] w-full max-w-xl animate-fade-up">
                <div className="absolute inset-x-10 bottom-0 h-24 rounded-[100%] bg-mint-500/10 blur-3xl" />
                <div className="absolute inset-y-0 inset-x-2 rounded-[2.5rem] bg-gradient-to-b from-white/[0.05] to-transparent" />
                <Avatar3D state={avatarState} />
              </div>
              <h1 className="mt-2 text-4xl font-extrabold tracking-tight sm:text-5xl"><span className="text-gradient">هستی</span></h1>
              <p className="mt-3 max-w-md text-sm leading-7 text-slate-400">یک دستیار هوش‌مصنوعی خصوصی که کاملاً روی سرور شما اجرا می‌شود.</p>
              <div className="mt-6 flex max-w-xl flex-wrap justify-center gap-2">
                {QUICK_PROMPTS.map((chip) => (
                  <button key={chip.label} onClick={() => send(chip.message)} className="rounded-full border border-white/10 bg-white/[0.05] px-4 py-2 text-[13px] text-slate-300 transition hover:border-mint-400/40 hover:bg-mint-500/10 hover:text-mint-300 active:scale-[0.97]">{chip.label}</button>
                ))}
              </div>
            </div>
          ) : (
            <div className="mx-auto flex min-h-full w-full max-w-3xl flex-col gap-6 px-4 py-8 sm:px-6">
              {messages.map((m) => (
                <div key={m.id} className={`flex animate-fade-up ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                  {m.role === "user" ? (
                    <div className="flex max-w-[85%] flex-col gap-1.5 items-end">
                      <div className="rounded-2xl rounded-br-md bg-gradient-to-l from-mint-500 to-teal-500 px-4 py-3 text-[14px] font-medium leading-7 text-night-950 whitespace-pre-wrap">{m.content}</div>
                    </div>
                  ) : (
                    <div className="flex items-start gap-2.5">
                      <div className="mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-mint-400 to-glow-500 shadow-glow"><Sparkles size={17} className="text-night-950" strokeWidth={2.4} /></div>
                      <div className="flex max-w-[85%] flex-col gap-1.5 items-start">
                        <div className="rounded-2xl rounded-br-md border border-white/10 bg-white/[0.05] px-4 py-3 text-[14px] leading-7 text-slate-200 backdrop-blur whitespace-pre-wrap">{m.content}</div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {pending && (
                <div className="flex animate-fade-up justify-start">
                  <div className="flex items-start gap-2.5">
                    <div className="mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-mint-400 to-glow-500 shadow-glow"><Sparkles size={17} className="text-night-950" strokeWidth={2.4} /></div>
                    <div className="flex items-center gap-1.5 rounded-2xl rounded-br-md border border-white/10 bg-white/[0.05] px-4 py-3.5 backdrop-blur">
                      <span className="typing-dot h-2 w-2 rounded-full bg-mint-300" /><span className="typing-dot h-2 w-2 rounded-full bg-mint-300" /><span className="typing-dot h-2 w-2 rounded-full bg-mint-300" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={endRef} />
            </div>
          )}
        </div>

        <div className="px-4 pb-5 sm:px-6">
          <form onSubmit={(e) => { e.preventDefault(); send(input); }} className="glass-deep mx-auto w-full max-w-3xl rounded-3xl p-3">
            <div className="flex items-end gap-2">
              <textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); } }} rows={1} placeholder="پیام خود را بنویسید…" className="max-h-36 min-h-[44px] flex-1 resize-none bg-transparent px-2 py-2.5 text-[15px] leading-6 text-slate-100 placeholder:text-slate-600 focus:outline-none" />
              <button type="submit" disabled={!input.trim() || pending} className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-mint-400 to-teal-500 text-night-950 shadow-glow transition enabled:hover:brightness-110 enabled:active:scale-95 disabled:cursor-not-allowed disabled:opacity-40">
                <Send size={19} strokeWidth={2.4} />
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
