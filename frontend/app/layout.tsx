import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CIVARA - SIH25031 MOOLKARAN Engine",
  description: "Geospatial decision support engine for land & resource management",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-slate-900 text-slate-100">{children}</body>
    </html>
  );
}
