"use client";

import React, { useEffect, useRef } from "react";

export type MolecularRepresentation = "cartoon" | "ball-stick" | "wireframe";

export interface MolViewerControls {
  rotate: (angle: number, axis?: "x" | "y" | "z") => void;
  zoom: (factor: number) => void;
  resetView: () => void;
}

export default function Mol3DViewport({ pdbData, representation, isSpinning, isSimulating, onWebGLError }: any) {
  const viewerRef = useRef<HTMLDivElement>(null);
  const viewerInstance = useRef<any>(null);

  useEffect(() => {
    if (!pdbData) return;
    const container = viewerRef.current;
    if (!container) return;

    let cancelled = false;

    (async () => {
      try {
        const mod: any = await import("3dmol");
        const $3Dmol = mod.default ?? mod;
        if (cancelled) return;

        if (viewerInstance.current) {
          try { viewerInstance.current.clear(); } catch {}
        }
        container.innerHTML = "";

        const viewer = $3Dmol.createViewer(container, {
          backgroundColor: "#050505",
        });
        viewerInstance.current = viewer;

        viewer.addModel(pdbData, "pdb");

        if (representation === "cartoon") {
          viewer.setStyle({}, { cartoon: { color: "spectrum" } });
        } else if (representation === "wireframe") {
          viewer.setStyle({}, { line: { linewidth: 2, color: "spectrum" } });
        } else {
          viewer.setStyle({}, { stick: { radius: 0.2, color: "spectrum" }, sphere: { scale: 0.3, color: "spectrum" } });
        }

        viewer.zoomTo();
        viewer.render();

        if (isSpinning) viewer.spin("y");
      } catch (e: any) {
        console.error("3D Viewer Error:", e);
        if (onWebGLError) onWebGLError(e.message);
      }
    })();

    return () => { cancelled = true; };
  }, [pdbData, representation, isSpinning]);

  return <div ref={viewerRef} className="h-full w-full" />;
}
