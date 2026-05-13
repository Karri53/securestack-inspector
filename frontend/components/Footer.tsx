// frontend/components/Footer.tsx
// Minimal footer with a credit line and a couple of links.

import { Shield } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-ink-700/50 py-12">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-6 sm:flex-row">
        <div className="flex items-center gap-2 text-sm text-ink-400">
          <Shield className="h-4 w-4 text-brand-400" />
          <span>
            SecureStack Inspector. Built by{" "}
            <span className="font-medium text-ink-200">Karrington Hall</span>
          </span>
        </div>
        <div className="flex items-center gap-6 text-sm text-ink-400">
          <a
            href="https://github.com/Karri53/securestack-inspector"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-ink-100 transition-colors"
          >
            GitHub
          </a>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-ink-100 transition-colors"
          >
            API docs
          </a>
        </div>
      </div>
    </footer>
  );
}
