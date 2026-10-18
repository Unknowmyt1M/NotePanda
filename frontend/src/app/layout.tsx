import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NotePanda 🐼 — Fast Study Notes, Formula Sheets & DPPs for JEE/NEET",
  description: "Instant access to handwritten notes, chapter revision sheets, DPPs, and formula sheets for Class 11, Class 12, JEE Main & Advanced, and NEET.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#090d16] text-gray-100 antialiased selection:bg-emerald-500/30 selection:text-emerald-300">
        {children}
      </body>
    </html>
  );
}
