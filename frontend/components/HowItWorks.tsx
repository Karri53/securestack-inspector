// frontend/components/HowItWorks.tsx
// Three-step process walkthrough. Numbered steps with a connecting line
// visually communicate "sequence" without needing words to say so.

const steps = [
  {
    number: "01",
    title: "Submit a repository",
    body: "Paste a public GitHub URL or upload a zipped project. The API enqueues a scan job and returns an ID immediately — no waiting on the request.",
  },
  {
    number: "02",
    title: "Isolated analysis",
    body: "A scanner worker clones the repo into a sandboxed container, runs four analyzers in parallel, and writes findings to Postgres as they complete.",
  },
  {
    number: "03",
    title: "Risk-scored report",
    body: "Findings roll up into a severity score with prioritized remediation guidance. Export as JSON for tooling or PDF for executive review.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="border-t border-ink-700/50 bg-ink-800/30 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-wider text-brand-400">
            How it works
          </p>
          <h2 className="mt-3 text-4xl font-bold tracking-tight text-ink-100 sm:text-5xl">
            From URL to executive report in three steps
          </h2>
        </div>

        <div className="mx-auto mt-16 grid max-w-5xl grid-cols-1 gap-8 md:grid-cols-3">
          {steps.map((step) => (
            <div key={step.number} className="relative">
              {/* Big translucent number — visual anchor for each step */}
              <div className="font-mono text-5xl font-bold text-brand-500/30">
                {step.number}
              </div>
              <h3 className="mt-4 text-xl font-semibold text-ink-100">
                {step.title}
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-ink-300">
                {step.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}