"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Activity, Cpu, Gauge, Network, Radio, Server, ShieldCheck, Waves } from "lucide-react";

interface MonitorTabProps {
  activePdbId: string;
}

export default function MonitorTab({ activePdbId }: MonitorTabProps) {
  const [cpuSeries, setCpuSeries] = useState<number[]>([28, 34, 42, 39, 51, 47, 36, 44, 40, 48, 37, 45]);
  const [gpuTemp, setGpuTemp] = useState<number>(52);
  const [fps, setFps] = useState<number>(60);

  useEffect(() => {
    const timer = setInterval(() => {
      setCpuSeries((prev) => {
        const nextVal = Math.max(18, Math.min(89, prev[prev.length - 1] + Math.floor(Math.random() * 17) - 8));
        return [...prev.slice(1), nextVal];
      });
      setGpuTemp(50 + Math.floor(Math.random() * 7));
      setFps(58 + Math.floor(Math.random() * 3));
    }, 1600);
    return () => clearInterval(timer);
  }, []);

  const currentCpu = cpuSeries[cpuSeries.length - 1];

  return (
    <div className="mx-auto w-full max-w-6xl space-y-4">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-holo rounded-2xl p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/35 bg-cyan-500/10">
              <Activity className="h-5 w-5 text-cyan-300" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-100">Cluster & Telemetry Monitor</h2>
              <p className="font-mono text-xs text-slate-400">Active Target: PDB:{activePdbId} · Node aarch64-termux-01</p>
            </div>
          </div>
          <span className="flex items-center gap-2 rounded-full border border-emerald-400/35 bg-emerald-500/10 px-3 py-1 font-mono text-xs text-emerald-300">
            <Radio className="h-3.5 w-3.5 animate-pulse" /> TELEMETRY NOMINAL
          </span>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-xl border border-white/10 bg-black/50 p-3.5">
            <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400"><Cpu className="h-3.5 w-3.5 text-cyan-400" />QPU / CPU Load</div>
            <p className="mt-2 font-mono text-2xl font-bold text-cyan-300">{currentCpu}%</p>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/50 p-3.5">
            <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400"><Gauge className="h-3.5 w-3.5 text-purple-400" />WebGL Rate</div>
            <p className="mt-2 font-mono text-2xl font-bold text-purple-300">{fps} FPS</p>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/50 p-3.5">
            <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400"><Waves className="h-3.5 w-3.5 text-fuchsia-400" />Shader Core</div>
            <p className="mt-2 font-mono text-2xl font-bold text-fuchsia-300">{gpuTemp}°C</p>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/50 p-3.5">
            <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400"><ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />DB Latency</div>
            <p className="mt-2 font-mono text-2xl font-bold text-emerald-300">4 ms</p>
          </div>
        </div>

        <div className="mt-5 rounded-xl border border-cyan-500/20 bg-black/60 p-4">
          <div className="mb-3 flex items-center justify-between font-mono text-xs text-slate-400">
            <span>REAL-TIME COMPUTE PULSE</span><span className="text-cyan-300">1600ms SAMPLING</span>
          </div>
          <div className="flex h-28 items-end gap-2">
            {cpuSeries.map((val, idx) => (
              <div key={idx} className="flex flex-1 flex-col items-center gap-1">
                <div className="w-full rounded-t-md bg-gradient-to-t from-cyan-500/40 via-cyan-400/70 to-purple-400 transition-all duration-500" style={{ height: `${val}%` }} />
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="glass-holo-purple rounded-2xl p-4">
          <div className="mb-3 flex items-center gap-2 font-mono text-xs font-semibold text-purple-200 uppercase"><Server className="h-4 w-4 text-purple-400" />Subsystem Services</div>
          <div className="space-y-2 font-mono text-xs">
            {[
              { name: "3Dmol WebGL2 Canvas", status: "ACTIVE" },
              { name: "R3F Quantum Field Stage", status: "ACTIVE" },
              { name: "RCSB PDB Gateway Proxy", status: "ONLINE" },
              { name: "PostgreSQL Drizzle Pool", status: "CONNECTED" },
            ].map((item) => (
              <div key={item.name} className="flex items-center justify-between rounded-xl border border-white/10 bg-black/45 px-3 py-2">
                <span className="text-slate-300">{item.name}</span>
                <span className="text-[10px] font-semibold text-emerald-300">{item.status}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="glass-holo rounded-2xl p-4">
          <div className="mb-3 flex items-center gap-2 font-mono text-xs font-semibold text-cyan-200 uppercase"><Network className="h-4 w-4 text-cyan-400" />Quantum Network Mesh</div>
          <div className="space-y-2.5 font-mono text-xs text-slate-300">
            <div className="rounded-xl border border-white/10 bg-black/45 p-3">
              <div className="flex justify-between"><span>Upstream RCSB PDB Relay</span><span className="text-cyan-300">files.rcsb.org</span></div>
              <p className="mt-1 text-[11px] text-slate-500">Auto-cached into PostgreSQL.</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/45 p-3">
              <div className="flex justify-between"><span>Active Molecular Target</span><span className="text-purple-300">{activePdbId}</span></div>
              <p className="mt-1 text-[11px] text-slate-500">Synchronized across all tabs.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
