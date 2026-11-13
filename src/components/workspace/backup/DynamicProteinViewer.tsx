"use client";
import dynamic from "next/dynamic";

const ProteinViewer = dynamic(
  () => import("./ProteinViewer"),
  { ssr: false, loading: () => <p className="text-xs text-cyan-400 p-4">Loading 3D Viewer...</p> }
);

export default ProteinViewer;
