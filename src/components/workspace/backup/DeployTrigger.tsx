"use client";
import { useState } from "react";
import { Rocket, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

export default function DeployTrigger() {
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleDeploy = async () => {
    setStatus("loading");
    try {
      const res = await fetch("/api/deploy", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        setStatus("success");
        setMessage("دستور دیپلوی ارسال شد. ربات در ترموکس در حال اجراست...");
      } else {
        setStatus("error");
        setMessage(data.error || "خطا در ارسال دستور");
      }
    } catch (err: any) {
      setStatus("error");
      setMessage(err.message);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4 p-6 rounded-2xl border border-cyan-500/20 bg-cyan-500/5">
      <button
        onClick={handleDeploy}
        disabled={status === "loading"}
        className="flex items-center gap-2 rounded-xl bg-cyan-500 px-6 py-3 font-bold text-black transition hover:bg-cyan-400 disabled:opacity-50"
      >
        {status === "loading" ? <Loader2 className="animate-spin" size={20} /> : <Rocket size={20} />}
        {status === "loading" ? "در حال ارسال..." : "دیپلوی سایت (Deploy-bot)"}
      </button>
      {status === "success" && <div className="flex items-center gap-2 text-emerald-400 text-sm"><CheckCircle2 size={16} /> {message}</div>}
      {status === "error" && <div className="flex items-center gap-2 text-red-400 text-sm"><AlertCircle size={16} /> {message}</div>}
    </div>
  );
}
