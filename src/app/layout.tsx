import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Elen-k Health OS",
  description: "AI-powered scientific law discovery platform",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Elen-k",
  },
};

export const viewport: Viewport = {
  themeColor: "#22d3ee",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" dir="ltr">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
