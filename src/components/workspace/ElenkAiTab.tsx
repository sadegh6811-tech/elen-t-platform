"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Bot, Loader2, Send, User, Trash2 } from "lucide-react";

interface ElenkAiTabProps {
  initialMessages?: any[];
  activePdbId?: string;
  onPdbGenerated?: (pdbId: string) => void;
}

export default function ElenkAiTab({ initialMessages = [], activePdbId = "1CRN", onPdbGenerated }: ElenkAiTabProps) {
  const [messages, setMessages] = useState<any[]>(initialMessages);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleClearChat = async () => {
    if (!confirm("آیا مطمئنید؟")) return;
    try {
      await fetch("/api/workspace", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "clear_ai" }) });
      setMessages([]);
    } catch (e) {}
  };

  const sendPrompt = async (promptText: string) => {
    const trimmed = promptText.trim();
    if (!trimmed || sending) return;
    
    setSending(true); 
    setInput("");
    
    const userMsg = { id: Date.now(), role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST", 
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });
      
      const data = await res.json();
      let replyContent = data.reply || data.message || "خطا در دریافت پاسخ.";
      let generatedPdbId = null;
      let pdbContentToSave = null;
      let pdbMetadata = null;

      const startIdx = replyContent.indexOf('{');
      const endIdx = replyContent.lastIndexOf('}');
      
      if (startIdx !== -1 && endIdx > startIdx) {
        try {
          const parsed = JSON.parse(replyContent.slice(startIdx, endIdx + 1));
          
          if (parsed.pdb_content) {
            pdbContentToSave = parsed.pdb_content;
            
            if (parsed.type === "DNA_CUBE_ORIGAMI") {
              generatedPdbId = `DNA_CUBE_${Date.now().toString().slice(-4)}`;
              pdbMetadata = { name: "DNA Origami Cube", classification: "DNA NANOTECH", atomCount: parsed.edges_count * 40, residueCount: parsed.edges_count * 20 };
              replyContent = `✅ تراشه DNA مکعبی با موفقیت طراحی شد!\n\n📦 تعداد لبه‌ها: ${parsed.edges_count}\n🧬 ساختار سه‌بعدی در تب Lab بارگذاری شد.`;
            } else if (parsed.sequence) {
              generatedPdbId = `DNA_${parsed.sequence.slice(0, 6)}`;
              pdbMetadata = { name: `Designed DNA (${parsed.length} nt)`, classification: "DNA SEQUENCE", atomCount: parsed.length * 2, residueCount: parsed.length };
              replyContent = `✅ توالی DNA طراحی شد!\n\n🧬 طول: ${parsed.length} نوکلئوتید\n📊 نسبت GC: ${(parsed.gc_ratio * 100).toFixed(0)}%\n\nساختار در تب Lab بارگذاری شد.`;
            }

            // ذخیره ساختار در دیتابیس
            if (generatedPdbId && pdbContentToSave) {
              await fetch("/api/lab/save", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: generatedPdbId, name: pdbMetadata?.name || "AI Generated DNA", pdbData: pdbContentToSave }),
              });
            }
          }
        } catch (e) {
          console.error("JSON Parse Error", e);
        }
      }

      setMessages((prev) => [...prev, { id: Date.now() + 1, role: "assistant", content: replyContent }]);
      
      if (generatedPdbId && onPdbGenerated) {
        setTimeout(() => onPdbGenerated(generatedPdbId), 1000);
      }

    } catch (e) {
      setMessages((prev) => [...prev, { id: Date.now() + 1, role: "assistant", content: "ارتباط با سرور برقرار نشد." }]);
    } finally { 
      setSending(false); 
    }
  };

  return (
    <div className="mx-auto w-full max-w-5xl space-y-4">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-holo-purple rounded-2xl p-4 sm:p-5">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Bot className="h-5 w-5 text-purple-300" />
            <h2 className="text-sm font-semibold text-slate-100">Elen-k.Ai Scientific Copilot</h2>
          </div>
          <button onClick={handleClearChat} className="flex items-center gap-1.5 rounded-lg border border-red-500/30 bg-red-500/10 px-2.5 py-1 text-xs text-red-300 hover:bg-red-500/20">
            <Trash2 className="h-3.5 w-3.5" /> <span className="hidden sm:inline">پاک کردن</span>
          </button>
        </div>

        <div className="cyber-scrollbar h-[320px] space-y-3 overflow-y-auto rounded-xl border border-white/10 bg-[#04040a] p-4">
          {messages.length === 0 && <div className="flex h-full items-center justify-center text-xs text-slate-500">تاریخچه خالی است.</div>}
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === "assistant" ? "items-start" : "flex-row-reverse items-start"}`}>
              <div className={`flex h-7 w-7 items-center justify-center rounded-lg border ${msg.role === "assistant" ? "border-purple-400/40 bg-purple-500/20 text-purple-300" : "border-cyan-400/40 bg-cyan-500/20 text-cyan-300"}`}>
                {msg.role === "assistant" ? <Bot className="h-3.5 w-3.5" /> : <User className="h-3.5 w-3.5" />}
              </div>
              <div className={`max-w-[82%] rounded-2xl px-3.5 py-2.5 text-xs ${msg.role === "assistant" ? "bg-purple-950/25 text-slate-200" : "bg-cyan-950/30 text-cyan-100"}`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          <div ref={endRef} />
        </div>

        <form onSubmit={(e) => { e.preventDefault(); sendPrompt(input); }} className="mt-3 flex gap-2">
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="مثلاً: یک تراشه DNA مکعبی طراحی کن..." className="flex-1 rounded-xl border border-purple-400/30 bg-black/65 px-3.5 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-purple-500" />
          <button type="submit" disabled={sending} className="rounded-xl bg-purple-500/30 hover:bg-purple-500/50 px-4 py-2.5 text-xs font-semibold text-white transition-colors">
            {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : "ارسال"}
          </button>
        </form>
      </motion.div>
    </div>
  );
}
