// frontend/components/Hero.tsx
// Above-the-fold hero. First impression — has to land in 2 seconds.
// The three pillars: clear name, clear value prop, clear call to action.

import { ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";

export default function Hero() {
  return (
    <section className="relative overflow-hidden hero-glow">
      {/* Layered grid pattern adds technical texture behind the text */}
      <div className="absolute inset-0 grid-pattern opacity-40" />

      <div className="relative mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:py-40">
        <div className="mx-auto max-w-3xl text-center animate-fade-in">
          {/* Eyebrow badge — signals "this is a real project, not a toy" */}
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-4 py-1.5 text-xs font-medium text-brand-400">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Aligned with CISA SBOM &amp; OWASP SCVS guidance</span>
          </div>

          {/* Headline. Big, tight tracking, gradient on the key phrase. */}
          <h1 className="mt-8 text-5xl font-bold tracking-tight text-ink-100 sm:text-6xl lg:text-7xl">
            See every risk in your{" "}
            <span className="bg-gradient-to-r from-brand-400 to-brand-600 bg-clip-text text-transparent">
              software supply chain
            </span>
          </h1>

          {/* Subhead. One sentence. Explains what + why. */}
          <p className="mt-8 text-lg leading-relaxed text-ink-300 sm:text-xl">
            SecureStack Inspector scans repositories for dependency vulnerabilities,
            Dockerfile security mistakes, and SBOM compliance — producing risk-scored
            executive reports in seconds.
          </p>

          {/* CTAs. Primary on the left, secondary on the right. */}
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/dashboard"
              className="group inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 px-6 py-3 text-sm font-semibold text-ink-900 shadow-lg shadow-brand-500/25 transition-all hover:shadow-xl hover:shadow-brand-500/40 hover:-translate-y-0.5"
            >
              Run your first scan
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-lg border border-ink-700 bg-ink-800/50 px-6 py-3 text-sm font-semibold text-ink-100 backdrop-blur transition-all hover:border-ink-500 hover:bg-ink-800"
            >
              Read the API docs
            </a>
          </div>

          {/* Quiet tech badge row — provides credibility without being loud */}
          <div className="mt-16 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-xs font-medium uppercase tracking-wider text-ink-400">
            <span>Python · FastAPI</span>
            <span className="hidden sm:inline text-ink-600">·</span>
            <span>Next.js · TypeScript</span>
            <span className="hidden sm:inline text-ink-600">·</span>
            <span>Docker · PostgreSQL</span>
            <span className="hidden sm:inline text-ink-600">·</span>
            <span>Redis · CI/CD</span>
          </div>
        </div>
      </div>
    </section>
  );
}