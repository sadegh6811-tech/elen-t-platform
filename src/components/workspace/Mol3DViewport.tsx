"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import type { GLViewer } from "3dmol";

export type MolecularRepresentation = "cartoon" | "ball-stick" | "wireframe";

export interface MolViewerControls {
  rotate: (angle: number, axis?: "x" | "y" | "z") => void;
  zoom: (factor: number) => void;
  resetView: () => void;
}

interface Mol3DViewportProps {
  pdbData: string;
  representation: MolecularRepresentation;
  isSpinning: boolean;
  isSimulating: boolean;
  onControlsReady?: (controls: MolViewerControls) => void;
  onWebGLError?: (msg: string) => void;
}

function applyNeonStyle(viewer: GLViewer, representation: MolecularRepresentation) {
  viewer.setStyle({}, {});
  if (representation === "cartoon") {
    viewer.setStyle({}, { cartoon: { color: "spectrum" } });
  } else if (representation === "ball-stick") {
    viewer.setStyle({}, { stick: { radius: 0.14, color: "spectrum" }, sphere: { scale: 0.28, color: "spectrum" } });
  } else {
    viewer.setStyle({}, { line: { linewidth: 2, color: "spectrum" } });
  }
  viewer.render();
}

export default function Mol3DViewport({ pdbData, representation, isSpinning, isSimulating, onControlsReady, onWebGLError }: Mol3DViewportProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<GLViewer | null>(null);
  const [webglReady, setWebglReady] = useState(false);
  const [initError, setInitError] = useState<string | null>(null);

  const emitControls = useCallback((viewer: GLViewer) => {
    if (!onControlsReady) return;
    onControlsReady({
      rotate: (angle, axis = "y") => { try { viewer.rotate(angle, axis, 260); viewer.render(); } catch {} },
      zoom: (factor) => { try { viewer.zoom(factor, 240); viewer.render(); } catch {} },
      resetView: () => { try { viewer.zoomTo({}, 380); viewer.render(); } catch {} },
    });
  }, [onControlsReady]);

  useEffect(() => {
    let active = true;
    const container = containerRef.current;
    if (!container) return;

    async function initViewer() {
      try {
        const mod: any = await import("3dmol");
        const createViewerFn = mod.createViewer ?? mod.default?.createViewer ?? (window as any).$3Dmol?.createViewer;
        if (!createViewerFn) throw new Error("3Dmol createViewer unavailable.");
        container.innerHTML = "";
        const viewer = createViewerFn(container, { backgroundColor: "#050505", antialias: true });
        if (!viewer) throw new Error("WebGL context failed.");
        viewerRef.current = viewer;
        setWebglReady(true);
        emitControls(viewer);
      } catch (err: any) {
        if (!active) return;
        setInitError(err.message);
        onWebGLError?.(err.message);
      }
    }

    initViewer();
    return () => {
      active = false;
      if (viewerRef.current) {
        try { viewerRef.current.clear(); } catch {}
        viewerRef.current = null;
      }
    };
  }, [emitControls, onWebGLError]);

  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || !webglReady || !pdbData) return;
    try {
      viewer.clear();
      viewer.addModel(pdbData, "pdb");
      applyNeonStyle(viewer, representation);
      viewer.zoomTo({}, 350);
      viewer.render();
      viewer.spin(isSpinning || isSimulating ? "y" : false, isSimulating ? 1.45 : 0.65);
    } catch (err: any) {
      setInitError(err.message);
    }
  }, [pdbData, representation, isSpinning, isSimulating, webglReady]);

  if (initError) {
    return <div className="flex h-full w-full items-center justify-center p-6 text-center text-sm text-red-400">⚠️ {initError}</div>;
  }

  return <div ref={containerRef} className="relative h-full w-full cursor-grab touch-none active:cursor-grabbing" />;
}
