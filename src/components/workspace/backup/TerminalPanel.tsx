import { useEffect, useRef, useState } from "react";
import { TerminalSquare, Pause, Play, RotateCcw } from "lucide-react";
import GlassPanel from "./GlassPanel";

export default function TerminalPanel() {
  const [lines, setLines] = useState<string[]>(["[sys] Real ELEN-T Engine Console\n"]);
  const [isRunning, setIsRunning] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [lines]);

  const runRealEngine = async () => {
    setIsRunning(true);
    setLines((prev) => [...prev, "\n🚀 Sending test data to ELEN-T Engine...\n"]);
    
    // داده تست
    const X = Array.from({length: 50}, (_, i) => [i+1, i+2]);
    const y = Array.from({length: 50}, (_, i) => 2*(i+1)+1);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/discover", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ X, y, features: ["a", "b"] })
      });
      const data = await res.json();
      
      setLines((prev) => [
        ...prev,
        `✅ Server Response:\n`,
        `   Success: ${data.success}`,
        `   Formula: ${data.formula}`,
        `   R²     : ${data.r2}`,
        `   Scaling: ${JSON.stringify(data.scaling)}\n`
      ]);
    } catch (err) {
      setLines((prev) => [...prev, `❌ Error: Failed to connect to bridge\n`]);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <GlassPanel accent="cyan" title="Super Termux" subtitle="موتور واقعی ELEN-T" icon={<TerminalSquare size={18} />}>
      <div className="flex flex-col h-full">
        <div className="p-4 border-b border-white/10">
          <button
            onClick={runRealEngine}
            disabled={isRunning}
            className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-3 rounded-xl transition-all disabled:opacity-50"
          >
            {isRunning ? "⏳ Engine is running..." : "⚡ Run Real ELEN-T Engine"}
          </button>
        </div>
        <div ref={scrollRef} className="flex-1 bg-black/80 p-4 font-mono text-sm text-cyan-300 overflow-y-auto" dir="ltr">
          {lines.map((line, i) => (
            <div key={i} className="whitespace-pre-wrap">{line}</div>
          ))}
        </div>
      </div>
    </GlassPanel>
  );
}
