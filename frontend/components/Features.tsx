// frontend/components/Features.tsx
// Four-card feature grid. Each card maps to one scanner type we'll build
// in later phases. Icons from lucide-react keep weight consistent.

import { Package, FileCode, ScrollText, Gauge } from "lucide-react";

// Data-driven so adding/removing cards is trivial. Each card is identical
// in structure — readability beats clever templating here.
const features = [
  {
    icon: Package,
    title: "Dependency analysis",
    description:
      "Parses requirements.txt, package.json, and pom.xml to identify vulnerable, outdated, or license-risky packages.",
  },
  {
    icon: FileCode,
    title: "Dockerfile linting",
    description:
      "Detects security antipatterns: running as root, latest tags, exposed secrets, missing healthchecks, and overprivileged users.",
  },
  {
    icon: ScrollText,
    title: "SBOM generation",
    description:
      "Produces CycloneDX-format software bills of materials, aligned with CISA guidance and ready for compliance reviews.",
  },
  {
    icon: Gauge,
    title: "Risk scoring",
    description:
      "Aggregates findings into a single severity score per repo, with prioritized remediation guidance for engineering teams.",
  },
];

export default function Features() {
  return (
    <section id="features" className="border-t border-ink-700/50 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6">
        {/* Section header. Eyebrow + headline + subhead — consistent rhythm. */}
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-wider text-brand-400">
            What it analyzes
          </p>
          <h2 className="mt-3 text-4xl font-bold tracking-tight text-ink-100 sm:text-5xl">
            Four scanners, one report
          </h2>
          <p className="mt-6 text-lg text-ink-300">
            Every scan runs all four analyzers in parallel inside isolated worker
            containers, then merges results into a single risk profile.
          </p>
        </div>

        {/* Responsive card grid — 1 col mobile, 2 col tablet, 4 col desktop */}
        <div className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-6 sm:grid-cols-2 lg:max-w-none lg:grid-cols-4">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group relative rounded-2xl border border-ink-700 bg-ink-800/50 p-6 backdrop-blur transition-all hover:border-brand-500/50 hover:bg-ink-800 hover:-translate-y-1"
            >
              {/* Icon container — gradient background, soft glow on hover */}
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500/20 to-brand-600/10 text-brand-400 transition-all group-hover:from-brand-500/30 group-hover:to-brand-600/20">
                <feature.icon className="h-6 w-6" strokeWidth={2} />
              </div>

              <h3 className="mt-5 text-base font-semibold text-ink-100">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-ink-300">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}