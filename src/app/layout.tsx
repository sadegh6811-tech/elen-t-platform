import type { Metadata, Viewport } from "next";
import { JetBrains_Mono, Space_Grotesk, Vazirmatn } from "next/font/google";
import type { ReactNode } from "react";
import { LanguageProvider } from "@/lib/LanguageContext";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space-grotesk", weight: ["400", "500", "600", "700"] });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains-mono", weight: ["400", "500", "600", "700"] });
const vazirmatn = Vazirmatn({ subsets: ["arabic"], variable: "--font-vazirmatn", weight: ["400", "500", "600", "700"] });

export const metadata: Metadata = {
  title: "Elen-k · Quantum Molecular Simulation Lab",
  description: "Advanced 3D WebGL Molecular Simulation Laboratory & Quantum Workspace.",
};

export const viewport: Viewport = {
  themeColor: "#050505",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" dir="ltr" className={`${spaceGrotesk.variable} ${jetbrainsMono.variable} ${vazirmatn.variable} dark`} suppressHydrationWarning>
      <body className="min-h-screen bg-[#050505] text-slate-100 antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
