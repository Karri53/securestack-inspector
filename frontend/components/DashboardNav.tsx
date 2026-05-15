// frontend/components/DashboardNav.tsx
// Top nav for /dashboard and its child routes. Similar visual to the
// landing page Navbar but different links - on the dashboard we don't
// have anchor sections to link to.

import Link from "next/link";
import { Github, Shield } from "lucide-react";

export default function DashboardNav() {
  return (
    <header className="sticky top-0 z-50 border-b border-ink-700/50 bg-ink-900/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 shadow-lg shadow-brand-500/20 transition-transform group-hover:scale-105">
            <Shield className="h-5 w-5 text-ink-900" strokeWidth={2.5} />
          </div>
          <span className="font-semibold tracking-tight text-ink-100">
            SecureStack <span className="text-brand-400">Inspector</span>
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-sm text-ink-300">
          <Link href="/" className="hover:text-ink-100 transition-colors">
            Home
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-ink-100 transition-colors"
          >
            API docs
          </a>
        </nav>

        <a
          href="https://github.com/Karri53/securestack-inspector"
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