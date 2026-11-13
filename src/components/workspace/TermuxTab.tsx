"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { ChevronRight, Loader2, TerminalSquare } from "lucide-react";
import type { TerminalEntry } from "@/db/schema";

interface TermuxTabProps {
  initialEntries: TerminalEntry[];
  activePdbId: string;
  onSyncPdb?: (pdbId: string) => void;
}

const QUICK_COMMANDS = [
  "help",
  "nvidia-smi",
  "status",
  "python3 sim_check.py",
  "pdb-fetch 1UBQ",
  "uname -a",
];

export default function TermuxTab({ initialEntries, activePdbId, onSyncPdb }: TermuxTabProps) {
  const [entries, setEntries] = useState<TerminalEntry[]>(initialEntries);
  const [command, setCommand] = useState("");
  const [running, setRunning] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [entries]);

  const executeCommand = async (rawCmd: string) => {
    const trimmed = rawCmd.trim();
    if (!trimmed || running) return;

    setRunning(true);
    setCommand("");

    try {
      const res = await fetch("/api/workspace", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "terminal", command: trimmed, activePdb: activePdbId }),
      });
      const data = await res.json();
      if (res.ok && data?.entry) {
        if (data.cleared) {
          setEntries([data.entry]);
        } else {
          setEntries((prev) => [...prev, data.entry]);
        }
      }

      if (trimmed.toLowerCase().startsWith("pdb-fetch")) {
        const target = trimmed.split(/\s+/)[1]?.toUpperCase();
        if (target && target.length >= 4) {
          onSyncPdb?.(target);
        }
      }
    } finally {
      setRunning(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeCommand(command);
  };

  return (
    <div className="mx-auto w-full max-w-5xl space-y-4">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-holo rounded-2xl p-4 sm:p-5">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-400/35 bg-cyan-500/10">
              <TerminalSquare className="h-4 w-4 text-cyan-300" />
            </div>
            <div>
              <h2 className="font-mono text-sm font-semibold text-slate-100">Termux Quantum Bridge</h2>
              <p className="font-mono text-[11px] text-slate-400">aarch64-linux-android · Target PDB:{activePdbId}</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {QUICK_COMMANDS.map((cmd) => (
              <button key={cmd} type="button" onClick={() => executeCommand(cmd)} className="rounded-lg border border-white/10 bg-white/[0.03] px-2.5 py-1 font-mono text-[10px] text-cyan-300 transition hover:border-cyan-400/40 hover:bg-cyan-500/15">
                {cmd}
              </button>
            ))}
          </div>
        </div>

        <div ref={scrollRef} className="cyber-scrollbar h-[340px] overflow-y-auto rounded-xl border border-cyan-500/20 bg-[#030408] p-4 font-mono text-xs leading-relaxed">
          {entries.map((entry) => (
            <div key={entry.id} className="mb-3">
              <div className="flex items-center gap-1.5 text-cyan-300">
                <span className="text-purple-400">termux@elen-k</span>
                <span className="text-slate-500">:~$</span>
                <span>{entry.command}</span>
              </div>
              <pre className="mt-1 whitespace-pre-wrap text-[11px] text-slate-300">{entry.output}</pre>
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="mt-3 flex gap-2">
          <div className="relative flex flex-1 items-center">
            <ChevronRight className="pointer-events-none absolute left-3 h-4 w-4 text-cyan-400" />
            <input
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              placeholder="Type command (try: help, status, pdb-fetch 1UBQ)..."
              className="w-full rounded-xl border border-cyan-500/25 bg-black/70 py-2.5 pr-3 pl-9 font-mono text-xs text-cyan-100 placeholder:text-slate-600 focus:border-cyan-400 focus:outline-none"
            />
          </div>
          <button type="submit" disabled={running} className="flex items-center gap-1.5 rounded-xl border border-cyan-400/45 bg-cyan-500/20 px-4 py-2.5 font-mono text-xs font-semibold text-cyan-200 transition hover:bg-cyan-500/30 disabled:opacity-50">
            {running ? <Loader2 className="h-4 w-4 animate-spin" /> : "EXEC"}
          </button>
        </form>
      </motion.div>
    </div>
  );
}
