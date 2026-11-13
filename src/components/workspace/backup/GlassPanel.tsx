import React from 'react';

interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
}

export default function GlassPanel({ children, className = '' }: GlassPanelProps) {
  return (
    <div className={`bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-4 shadow-lg ${className}`}>
      {children}
    </div>
  );
}
