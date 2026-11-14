"use client";

import React, { useCallback, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { Atom, Activity, Loader2, Search, AlertCircle } from "lucide-react";
import { PRESET_MOLECULES, sanitizePdbId } from "@/lib/pdbUtils";
import type { MolecularRepresentation } from "@/components/workspace/Mol3DViewport";

const Mol3DViewport = dynamic(() => import("@/components/workspace/Mol3DViewport"), {
  ssr: false,
  loading: () => <div className="flex h-full w-full items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-cyan-400" /></div>,
});

export default function MolecularLab({ activePdbId: externalPdbId, onActivePdbChange }: any) {
  const [pdbData, setPdbData] = useState<string>("");
  const [representation, setRepresentation] = useState<MolecularRepresentation>("ball-stick");
  const [pdbInput, setPdbInput] = useState<string>(externalPdbId || "DNA_HELIX_01");
  const [loadedPdbId, setLoadedPdbId] = useState<string>("");
  const [meta, setMeta] = useState<any>(null);
  const [isLoadingPdb, setIsLoadingPdb] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [webglError, setWebglError] = useState<string | null>(null);

  const loadPdbStructure = useCallback(async (rawId: string) => {
    const cleanId = sanitizePdbId(rawId);
    if (!cleanId || cleanId.length < 3) {
      setError("شناسه نامعتبر است.");
      return;
    }

    setIsLoadingPdb(true);
    setError(null);
    setWebglError(null);
    setPdbInput(cleanId);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);

    try {
      const res = await fetch(`/api/lab/pdb?id=${encodeURIComponent(cleanId)}&t=${Date.now()}`, {
        cache: "no-store",
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      const payload = await res.json();
      
      if (!res.ok) throw new Error(payload?.error || `خطا در دریافت ${cleanId}`);

      setPdbData(payload.pdbData);
      setLoadedPdbId(payload.pdbId);
      onActivePdbChange?.(payload.pdbId);
      setMeta(payload);

      if (payload.pdbId.startsWith("DNA_CUBE")) {
        setRepresentation("ball-stick");
      } else {
        setRepresentation("cartoon");
      }

    } catch (err: any) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') setError("زمان انتظار به پایان رسید. VPN را چک کنید.");
      else setError(err.message || "خطا در بارگذاری");
      setPdbData("");
    } finally {
      setIsLoadingPdb(false);
    }
  }, [onActivePdbChange]);

  useEffect(() => {
    loadPdbStructure(externalPdbId || "DNA_HELIX_01");
  }, []);

  useEffect(() => {
    if (externalPdbId && externalPdbId !== loadedPdbId) {
      loadPdbStructure(externalPdbId);
    }
  }, [externalPdbId]);

  return (
    <div className="mx-auto w-full max-w-[1440px] space-y-4">
      <div className="glass-holo flex flex-wrap items-center justify-between gap-3 rounded-2xl px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/35 bg-cyan-500/10"><Atom className="h-5 w-5 text-cyan-300" /></div>
          <div>
            <h1 className="text-sm font-semibold text-slate-100 sm:text-base">Quantum Molecular Simulation Lab</h1>
            <p className="font-mono text-[11px] text-slate-400">{meta ? `${meta.pdbId} · ${meta.name} (${meta.atomCount} atoms)` : "Synchronizing..."}</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          {PRESET_MOLECULES.map((p) => (
            <button key={p.pdbId} type="button" onClick={() => loadPdbStructure(p.pdbId)} disabled={isLoadingPdb}
              className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1 font-mono text-[11px] transition-all ${loadedPdbId === p.pdbId ? "border-cyan-400/70 bg-cyan-500/20 text-cyan-200" : "border-white/10 bg-white/[0.03] text-slate-400 hover:border-purple-400/40"}`}>
              <span>{p.pdbId}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <div className="order-3 space-y-4 lg:order-1 lg:col-span-3">
          <div className="glass-holo rounded-2xl p-4">
            <div className="mb-3 flex items-center gap-2"><Activity className="h-4 w-4 text-cyan-400" /><h2 className="font-mono text-xs font-semibold uppercase text-slate-200">System Status</h2></div>
            <div className="space-y-3">
              <div><div className="mb-1 flex justify-between font-mono text-[11px]"><span className="text-slate-300">CPU</span><span className="text-cyan-300">34%</span></div><div className="h-1.5 rounded-full bg-slate-800"><motion.div className="h-full rounded-full bg-cyan-400" animate={{ width: "34%" }} /></div></div>
              <div><div className="mb-1 flex justify-between font-mono text-[11px]"><span className="text-slate-300">Memory</span><span className="text-purple-300">46%</span></div><div className="h-1.5 rounded-full bg-slate-800"><motion.div className="h-full rounded-full bg-purple-400" animate={{ width: "46%" }} /></div></div>
            </div>
          </div>
        </div>

        <div className="order-1 lg:order-2 lg:col-span-5">
          <div className="glass-holo relative flex w-full flex-col overflow-hidden rounded-2xl" style={{ height: "500px" }}>
            <div className="relative z-10 flex-1 w-full min-h-[300px]">
              <Mol3DViewport pdbData={pdbData} representation={representation} isSpinning={true} isSimulating={false} onControlsReady={() => {}} onWebGLError={(m: string) => setWebglError(m)} />
            </div>
            
            {/* --- جعبه دیباگ (فقط برای پیدا کردن مشکل) --- */}
            <div className="absolute top-0 left-0 z-50 bg-black/80 p-2 text-[8px] text-green-400 overflow-hidden w-full h-24 border-b border-green-500/30 pointer-events-none">
               <p>Length: {pdbData?.length || 0}</p>
               <p className="break-all">{pdbData?.slice(0, 150)}...</p>
            </div>
            {/* ------------------------------------------- */}

            {isLoadingPdb && (
              <div className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-[#050505]/80">
                <Loader2 className="h-10 w-10 animate-spin text-cyan-400" />
                <p className="mt-4 font-mono text-xs text-cyan-200">Fetching {pdbInput}...</p>
              </div>
            )}
            {error && !isLoadingPdb && (
              <div className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-[#050505]/80 p-6 text-center backdrop-blur-sm">
                 <AlertCircle className="h-10 w-10 text-rose-500 mb-3" />
                 <p className="text-rose-400 text-xs font-mono">{error}</p>
              </div>
            )}
            {webglError && !isLoadingPdb && !error && (
              <div className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-[#050505]/80 p-6 text-center backdrop-blur-sm">
                 <AlertCircle className="h-10 w-10 text-amber-500 mb-3" />
                 <p className="text-amber-400 text-xs font-mono">WebGL Error: {webglError}</p>
              </div>
            )}
          </div>
        </div>

        <div className="order-2 flex flex-col gap-4 lg:order-3 lg:col-span-4">
          <div className="glass-holo rounded-2xl p-4">
            <div className="mb-3 flex items-center gap-2"><Search className="h-4 w-4 text-cyan-400" /><h2 className="font-mono text-xs font-semibold uppercase text-slate-200">Load Structure</h2></div>
            <form onSubmit={(e) => { e.preventDefault(); loadPdbStructure(pdbInput); }} className="flex gap-2">
              <input type="text" value={pdbInput} onChange={(e) => setPdbInput(e.target.value.toUpperCase())} className="flex-1 rounded-xl border border-cyan-500/25 bg-black/60 py-2.5 pl-3 pr-3 font-mono text-sm text-cyan-100 focus:border-cyan-400 focus:outline-none" placeholder="DNA_HELIX_01" />
              <button type="submit" disabled={isLoadingPdb} className="rounded-xl border border-cyan-400/50 bg-cyan-500/25 px-4 py-2.5 font-mono text-xs font-semibold text-cyan-200 disabled:opacity-50">
                {isLoadingPdb ? <Loader2 className="h-4 w-4 animate-spin" /> : "LOAD"}
              </button>
            </form>

            <div className="mt-4 grid grid-cols-3 gap-2">
              {(["cartoon", "ball-stick", "wireframe"] as const).map((r) => (
                <button key={r} onClick={() => setRepresentation(r)} className={`rounded-xl border px-2 py-2 text-center transition ${representation === r ? "border-cyan-400/75 bg-cyan-500/20 text-cyan-200" : "border-white/10 bg-black/40 text-slate-400 hover:border-purple-400/40"}`}>
                  <span className="font-mono text-[11px] font-semibold">{r === "cartoon" ? "کارتونی" : r === "ball-stick" ? "توپ و میله" : "سیمی"}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
