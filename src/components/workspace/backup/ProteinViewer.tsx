"use client";
import { useEffect, useRef, useState } from "react";
import { Dna, Loader2, RotateCw, Download } from "lucide-react";

const SAMPLE_SEQ = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL";

export default function ProteinViewer() {
  const [sequence, setSequence] = useState(SAMPLE_SEQ);
  const [pdb, setPdb] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [stats, setStats] = useState<{ length: number; residues: number } | null>(null);
  const viewerRef = useRef<HTMLDivElement>(null);
  const viewerInstance = useRef<any>(null);

  useEffect(() => {
    if (!pdb || !viewerRef.current) return;
    let cancelled = false;
    (async () => {
      try {
        const mod: any = await import("3dmol");
        const $3Dmol = mod.default ?? mod;
        if (cancelled) return;
        viewerRef.current!.innerHTML = "";
        if (viewerInstance.current) { try { viewerInstance.current.clear(); } catch {} }
        const viewer = $3Dmol.createViewer(viewerRef.current, { backgroundColor: "#050505" });
        viewerInstance.current = viewer;
        viewer.addModel(pdb, "pdb");
        viewer.setStyle({}, { cartoon: { color: "spectrum" } });
        viewer.zoomTo();
        viewer.render();
      } catch (e: any) { if (!cancelled) setError(`3D viewer failed: ${e.message}`); }
    })();
    return () => { cancelled = true; };
  }, [pdb]);

  const handlePredict = async () => {
    setLoading(true); setError(""); setPdb(null); setStats(null);
    try {
      const res = await fetch("/api/lab/protein", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sequence }),
      });
      const data = await res.json();
      if (data.success) { setPdb(data.pdb); setStats({ length: data.length, residues: data.residues }); }
      else { setError(data.error || "Unknown error"); }
    } catch (e: any) { setError(e.message || "Network error"); }
    finally { setLoading(false); }
  };

  const handleSpin = () => { if (viewerInstance.current) viewerInstance.current.spin("y"); };
  const handleDownload = () => {
    if (!pdb) return;
    const blob = new Blob([pdb], { type: "chemical/x-pdb" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "elen-k-protein.pdb"; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Dna className="text-cyan-400" size={18} />
        <h3 className="text-sm font-bold text-white">Protein Structure Prediction</h3>
        <span className="ml-auto rounded-full bg-cyan-500/10 px-2 py-0.5 text-[10px] font-mono text-cyan-300">ESMFold</span>
      </div>
      <div>
        <div className="mb-1 flex items-center justify-between">
          <label className="text-[11px] font-mono uppercase tracking-widest text-slate-500">Amino Acid Sequence</label>
          <button onClick={() => setSequence(SAMPLE_SEQ)} className="text-[10px] text-cyan-400 hover:text-cyan-300">Load sample</button>
        </div>
        <textarea value={sequence} onChange={(e) => setSequence(e.target.value)} placeholder="MKTAYIAKQRQISFVKSHFSRQ..." maxLength={400} className="h-24 w-full rounded-xl border border-white/10 bg-[#0a0a12] p-3 font-mono text-xs text-white outline-none focus:border-cyan-500/60" />
        <div className="mt-1 flex justify-between text-[10px] text-slate-500">
          <span>{sequence.length} / 400 residues</span>
          <span>~{Math.max(5, Math.ceil(sequence.length / 50))}s ETA</span>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        <button onClick={handlePredict} disabled={loading || sequence.length < 10} className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-cyan-600 to-cyan-500 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-cyan-500/30 transition-opacity disabled:opacity-40">
          {loading ? <Loader2 className="animate-spin" size={14} /> : <Dna size={14} />}
          {loading ? "Folding..." : "Predict Structure"}
        </button>
        {pdb && (
          <>
            <button onClick={handleSpin} className="flex items-center gap-1 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300 hover:bg-white/10"><RotateCw size={14} /> Spin</button>
            <button onClick={handleDownload} className="flex items-center gap-1 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300 hover:bg-white/10"><Download size={14} /> PDB</button>
          </>
        )}
      </div>
      {error && <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-300">⚠️ {error}</div>}
      {stats && (
        <div className="flex gap-4 text-[11px] font-mono text-slate-400">
          <span>🧬 Length: <b className="text-cyan-300">{stats.length}</b></span>
          <span>⚛️ Atoms: <b className="text-cyan-300">{stats.residues}</b></span>
        </div>
      )}
      <div ref={viewerRef} className="h-[400px] w-full overflow-hidden rounded-xl border border-white/10 bg-[#050505] shadow-[0_0_40px_-15px_rgba(34,211,238,0.3)]" />
    </div>
  );
}
