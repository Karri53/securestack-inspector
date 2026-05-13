// frontend/components/Navbar.tsx
// Top navigation. Sticky on scroll with a subtle backdrop blur — looks
// premium and keeps the brand visible as users scroll through the landing.

import Link from "next/link";
import { Shield, Github } from "lucide-react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-ink-700/50 bg-ink-900/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        {/* Brand mark — icon + wordmark. Always link the logo home. */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 shadow-lg shadow-brand-500/20 transition-transform group-hover:scale-105">
            <Shield className="h-5 w-5 text-ink-900" strokeWidth={2.5} />
          </div>
          <span className="font-semibold tracking-tight text-ink-100">
            SecureStack <span className="text-brand-400">Inspector</span>
          </span>
        </Link>

        {/* Nav links — keep this list short. Crowded navs feel cheap. */}
        <nav className="hidden md:flex items-center gap-8 text-sm text-ink-300">
          <Link href="#features" className="hover:text-ink-100 transition-colors">
            Features
          </Link>
          <Link href="#how-it-works" className="hover:text-ink-100 transition-colors">
            How it works
          </Link>
          <Link href="#architecture" className="hover:text-ink-100 transition-colors">
            Architecture
          </Link>
        </nav>

        {/* Primary CTA. The GitHub button doubles as social proof. */}
        <a
          href="https://github.com/YOUR-USERNAME/securestack-inspector"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 rounded-lg border border-ink-700 bg-ink-800 px-4 py-2 text-sm font-medium text-ink-100 transition-all hover:border-brand-500/50 hover:bg-ink-700"
        >
          <Github className="h-4 w-4" />
          <span className="hidden sm:inline">View on GitHub</span>
        </a>
      </div>
    </header>
  );
}