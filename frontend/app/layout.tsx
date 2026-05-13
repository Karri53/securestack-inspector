// frontend/app/layout.tsx
// Root layout that wraps every page. Sets up fonts, metadata, and the
// global background. Next.js App Router convention — this is the
// equivalent of index.html in classic React apps.

import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

// next/font self-hosts Google Fonts at build time. No layout shift,
// no extra network requests, no Google tracking — purely better than
// linking from fonts.googleapis.com.
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

// SEO + social sharing metadata. When this URL gets shared on Slack/Twitter,
// these are the values that fill out the preview card.
export const metadata: Metadata = {
  title: "SecureStack Inspector — Software Supply Chain Risk Analyzer",
  description:
    "Containerized risk analyzer that scans repositories for dependency vulnerabilities, Dockerfile security issues, and SBOM compliance.",
  keywords: ["SBOM", "supply chain security", "Dockerfile", "vulnerability scanner"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans antialiased min-h-screen bg-ink-900 text-ink-100">
        {children}
      </body>
    </html>
  );
}