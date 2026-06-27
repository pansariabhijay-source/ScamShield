import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ScamShield AI — Can I trust this?",
  description:
    "Before you click, pay, scan, or trust something online, ScamShield tells you whether you should. Paste a message, upload a screenshot, or scan a QR code for an instant, human-readable trust verdict.",
  keywords: ["scam detection", "phishing", "UPI fraud", "KYC scam", "AI safety", "India"],
  openGraph: {
    title: "ScamShield AI — Can I trust this?",
    description: "Instant, human-readable trust verdicts for any suspicious message, link, or QR code.",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: "#ffffff",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
