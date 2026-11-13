"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, CheckCircle2, Loader2, AlertCircle } from "lucide-react";

interface UploadedFile {
  id: number;
  filename: string;
  row_count: number;
  status: string;
  uploaded_at: string;
}

export default function FileUploader() {
  const [uploading, setUploading] = useState(false);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [message, setMessage] = useState<{ type: "ok" | "err"; text: string } | null>(null);

  const fetchFiles = async () => {
    const res = await fetch("/api/upload", { cache: "no-store" });
    const json = await res.json();
    if (json.success) setFiles(json.files);
  };

  useEffect(() => {
    fetchFiles();
    const id = setInterval(fetchFiles, 5000);
    return () => clearInterval(id);
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setMessage(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/upload", { method: "POST", body: formData });
      const json = await res.json();
      if (json.success) {
        setMessage({ type: "ok", text: `✅ ${file.name} آپلود شد. Elen-t در صف پردازش است.` });
        fetchFiles();
      } else {
        setMessage({ type: "err", text: `❌ ${json.error}` });
      }
    } catch (err: any) {
      setMessage({ type: "err", text: `❌ خطا: ${err.message}` });
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  return (
    <div className="space-y-4">
      <label className="group flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-cyan-500/30 bg-cyan-500/5 p-6 transition-colors hover:border-cyan-400 hover:bg-cyan-500/10">
        <input type="file" accept=".csv" onChange={handleUpload} disabled={uploading} className="hidden" />
        {uploading ? (
          <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
        ) : (
          <Upload className="h-8 w-8 text-cyan-400 transition-transform group-hover:-translate-y-1" />
        )}
        <p className="mt-2 text-sm font-semibold text-cyan-300">
          {uploading ? "در حال آپلود..." : "آپلود فایل CSV"}
        </p>
        <p className="mt-1 text-xs text-slate-500">حداکثر ۲ مگابایت · فقط .csv</p>
      </label>

      {message && (
        <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className={`rounded-lg border px-3 py-2 text-xs ${message.type === "ok" ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300" : "border-red-500/40 bg-red-500/10 text-red-300"}`}>
          {message.text}
        </motion.div>
      )}

      <div className="rounded-2xl border border-white/5 bg-[#0a0a12]/80 p-3">
        <h3 className="mb-2 text-xs font-mono uppercase tracking-widest text-slate-500">آرشیو دیتاست‌ها</h3>
        {files.length === 0 ? (
          <p className="text-xs text-slate-600">هنوز فایلی آپلود نشده است.</p>
        ) : (
          <ul className="space-y-1.5 max-h-48 overflow-y-auto">
            {files.map((f) => (
              <li key={f.id} className="flex items-center justify-between rounded-lg bg-white/5 px-2 py-1.5 text-xs">
                <div className="flex items-center gap-2 text-slate-300">
                  <FileText className="h-3.5 w-3.5 text-cyan-400" />
                  <span className="truncate max-w-[120px]">{f.filename}</span>
                  <span className="text-slate-600">({f.row_count} rows)</span>
                </div>
                <StatusBadge status={f.status} />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { icon: React.ReactNode; cls: string; label: string }> = {
    pending: { icon: <Loader2 className="h-3 w-3 animate-spin" />, cls: "text-amber-300", label: "در صف" },
    processing: { icon: <Loader2 className="h-3 w-3 animate-spin" />, cls: "text-cyan-300", label: "در حال تحلیل" },
    done: { icon: <CheckCircle2 className="h-3 w-3" />, cls: "text-emerald-300", label: "تکمیل" },
    failed: { icon: <AlertCircle className="h-3 w-3" />, cls: "text-red-300", label: "خطا" },
  };
  const s = map[status] ?? map.pending;
  return <span className={`flex items-center gap-1 ${s.cls}`}>{s.icon}{s.label}</span>;
}
