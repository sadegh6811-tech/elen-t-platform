"use client";

import React, { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Activity, Atom, Bot, Cpu, Rocket, TerminalSquare, Languages } from "lucide-react";
import MolecularLab from "@/components/workspace/MolecularLab";
import MonitorTab from "@/components/workspace/MonitorTab";
import DeployBotTab from "@/components/workspace/DeployBotTab";
import TermuxTab from "@/components/workspace/TermuxTab";
import ElenkAiTab from "@/components/workspace/ElenkAiTab";
import { useLanguage } from "@/lib/LanguageContext";
import type { AiMessage, SimulationRun, TerminalEntry, WorkspaceDeployment } from "@/db/schema";

export type WorkspaceTabId = "monitor" | "deploy-bot" | "lab" | "termux" | "elenk-ai";

interface ElenkWorkspaceProps {
  initialRuns: SimulationRun[];
  initialDeployments: WorkspaceDeployment[];
  initialTerminal: TerminalEntry[];
  initialAiMessages: AiMessage[];
}

const NAV_TABS = [
  { id: "monitor" as const, labelEn: "Monitor", labelFa: "مانیتور", icon: Activity, accent: "cyan" },
  { id: "deploy-bot" as const, labelEn: "Deploy-bot", labelFa: "دیپلوی", icon: Rocket, accent: "purple" },
  { id: "lab" as const, labelEn: "Lab", labelFa: "آزمایشگاه", icon: Atom, accent: "cyan" },
  { id: "termux" as const, labelEn: "Termux", labelFa: "ترموکس", icon: TerminalSquare, accent: "cyan" },
  { id: "elenk-ai" as const, labelEn: "Elen-k.Ai", labelFa: "ال-کی.ای", icon: Bot, accent: "purple" },
];

export default function ElenkWorkspace({ initialRuns, initialDeployments, initialTerminal, initialAiMessages }: ElenkWorkspaceProps) {
  const [activeTab, setActiveTab] = useState<WorkspaceTabId>("lab");
  const [activePdbId, setActivePdbId] = useState<string>("1CRN");
  const { lang, setLang, t } = useLanguage();

  const handleSyncPdbFromTermux = (pdbId: string) => {
    setActivePdbId(pdbId);
    setActiveTab("lab");
  };

  return (
    <div className="bg-holo-grid relative flex min-h-screen flex-col text-slate-100">
      <header className="sticky top-0 z-40 border-b border-cyan-500/15 bg-[#050505]/85 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1440px] items-center justify-between px-4 py-2.5 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-400/45 bg-gradient-to-br from-cyan-500/20 to-purple-600/25">
              <Cpu className="h-4 w-4 text-cyan-300" />
            </div>
            <div>
              <span className="text-sm font-bold tracking-wider text-white uppercase sm:text-base">ELEN-K</span>
              <p className="hidden font-mono text-[10px] text-slate-400 sm:block">
                {t("Bio-Molecular Simulation Workspace", "فضای کاری شبیه‌سازی بیو-مولکولی")}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="rounded-full border border-purple-400/35 bg-purple-500/10 px-3 py-1 font-mono text-[11px] text-purple-200">
              PDB:{activePdbId}
            </span>
            <button
              onClick={() => setLang(lang === "fa" ? "en" : "fa")}
              className="flex items-center gap-1.5 rounded-full border border-cyan-400/40 bg-cyan-500/10 px-2.5 py-1 font-mono text-[11px] text-cyan-200 transition hover:bg-cyan-500/20"
              title={t("Switch to Persian", "تغییر به انگلیسی")}
            >
              <Languages className="h-3.5 w-3.5" />
              <span>{lang === "fa" ? "EN" : "FA"}</span>
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 px-3 pt-4 pb-28 sm:px-6 sm:pt-5 sm:pb-28">
        <AnimatePresence mode="wait">
          <motion.div key={activeTab} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.2 }}>
            {activeTab === "lab" && <MolecularLab initialRuns={initialRuns} activePdbId={activePdbId} onActivePdbChange={setActivePdbId} />}
            {activeTab === "monitor" && <MonitorTab activePdbId={activePdbId} />}
            {activeTab === "deploy-bot" && <DeployBotTab initialDeployments={initialDeployments} />}
            {activeTab === "termux" && <TermuxTab initialEntries={initialTerminal} activePdbId={activePdbId} onSyncPdb={handleSyncPdbFromTermux} />}
            {activeTab === "elenk-ai" && <ElenkAiTab initialMessages={initialAiMessages} activePdbId={activePdbId} />}
          </motion.div>
        </AnimatePresence>
      </main>

      <nav className="fixed inset-x-0 bottom-0 z-50 border-t border-cyan-500/20 bg-[#050508]/92 px-2 pt-1.5 pb-[max(0.5rem,env(safe-area-inset-bottom))] backdrop-blur-2xl">
        <div className="mx-auto flex max-w-2xl items-center justify-around gap-1">
          {NAV_TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            const label = lang === "fa" ? tab.labelFa : tab.labelEn;
            return (
              <button key={tab.id} type="button" onClick={() => setActiveTab(tab.id)}
                className={`relative flex flex-1 flex-col items-center justify-center rounded-2xl py-2 transition-colors ${isActive ? "text-cyan-200" : "text-slate-400 hover:text-slate-200"}`}>
                {isActive && <motion.div layoutId="activeNavPill" className={`absolute inset-x-1 inset-y-0.5 rounded-2xl border ${tab.accent === "purple" ? "border-purple-400/50 bg-purple-500/18" : "border-cyan-400/50 bg-cyan-500/18"}`} />}
                <Icon className={`relative z-10 h-5 w-5 ${isActive ? "text-cyan-300" : ""}`} />
                <span className={`relative z-10 mt-1 font-mono text-[10px] ${isActive ? "font-semibold text-white" : "font-medium"}`}>{label}</span>
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
