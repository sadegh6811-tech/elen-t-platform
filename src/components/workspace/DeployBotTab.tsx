"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, GitBranch, Loader2, Power, Rocket, ServerCog } from "lucide-react";
import type { WorkspaceDeployment } from "@/db/schema";

interface DeployBotTabProps {
  initialDeployments: WorkspaceDeployment[];
}

export default function DeployBotTab({ initialDeployments }: DeployBotTabProps) {
  const [deployments, setDeployments] = useState<WorkspaceDeployment[]>(initialDeployments);
  const [busyId, setBusyId] = useState<number | null>(null);

  const handleDeploy = async (id: number) => {
    setBusyId(id);
    try {
      const res = await fetch("/api/workspace", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "deploy", id }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data?.deployment) {
          setDeployments((prev) => prev.map((d) => (d.id === id ? data.deployment : d)));
        }
      }
    } finally { setBusyId(null); }
  };

  const handleToggle = async (id: number) => {
    setBusyId(id);
    try {
      const res = await fetch("/api/workspace", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "toggle_deploy", id }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data?.deployment) {
          setDeployments((prev) => prev.map((d) => (d.id === id ? data.deployment : d)));
        }
      }
    } finally { setBusyId(null); }
  };

  return (
    <div className="mx-auto w-full max-w-5xl space-y-4">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-holo rounded-2xl p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-purple-400/35 bg-purple-500/15">
              <Rocket className="h-5 w-5 text-purple-300" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-100">Deploy-bot Pipeline Orchestrator</h2>
              <p className="font-mono text-xs text-slate-400">Autonomous Molecular Compute & Edge Mesh Nodes</p>
            </div>
          </div>
          <span className="rounded-full border border-cyan-400/30 bg-cyan-500/10 px-3 py-1 font-mono text-[11px] text-cyan-300">
            {deployments.filter((d) => d.status === "live").length}/{deployments.length} NODES LIVE
          </span>
        </div>

        <div className="mt-5 grid grid-cols-1 gap-3 md:grid-cols-3">
          {deployments.map((item) => {
            const isLive = item.status === "live";
            const isBusy = busyId === item.id;
            return (
              <div key={item.id} className="flex flex-col justify-between rounded-2xl border border-white/10 bg-black/55 p-4 transition hover:border-cyan-400/35">
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <ServerCog className="h-4 w-4 text-cyan-400" />
                      <h3 className="font-mono text-xs font-semibold text-slate-100">{item.serviceName}</h3>
                    </div>
                    <span className={`rounded-full px-2 py-0.5 font-mono text-[10px] uppercase ${isLive ? "border border-emerald-400/40 bg-emerald-500/15 text-emerald-300" : "border border-amber-400/40 bg-amber-500/15 text-amber-300"}`}>
                      {item.status}
                    </span>
                  </div>
                  <div className="mt-3 space-y-1.5 font-mono text-[11px] text-slate-400">
                    <div className="flex items-center gap-1.5">
                      <GitBranch className="h-3.5 w-3.5 text-purple-400" />
                      <span>{item.branch}</span>
                      <span className="text-slate-600">·</span>
                      <span className="text-cyan-300">{item.commitHash}</span>
                    </div>
                    <p className="text-slate-500">Cluster: {item.environment}</p>
                  </div>
                </div>
                <div className="mt-4 flex gap-2">
                  <button type="button" disabled={isBusy} onClick={() => handleDeploy(item.id)} className="flex flex-1 items-center justify-center gap-1.5 rounded-xl border border-cyan-400/40 bg-cyan-500/15 px-3 py-2 font-mono text-[11px] font-semibold text-cyan-200 transition hover:bg-cyan-500/25 disabled:opacity-50">
                    {isBusy ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CheckCircle2 className="h-3.5 w-3.5" />}
                    <span>Redeploy</span>
                  </button>
                  <button type="button" disabled={isBusy} onClick={() => handleToggle(item.id)} className="rounded-xl border border-white/15 bg-white/[0.04] p-2 text-slate-300 transition hover:border-purple-400/50 hover:text-purple-200 disabled:opacity-50" title={isLive ? "Set Standby" : "Activate Node"}>
                    <Power className="h-4 w-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
