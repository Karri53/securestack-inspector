// frontend/components/StatusDashboard.tsx
// Live API status panel. Pings /health every 10s and shows the result.
// This is the bridge between the landing page and the actual product —
// proves the backend is real and gives recruiters something to interact with.

"use client";  // This component uses browser-only hooks (useEffect, useState)

import { useEffect, useState } from "react";
import { Activity, AlertCircle, CheckCircle2, Database } from "lucide-react";

// Shape of the response from GET /health. Keep in sync with backend.
type HealthResponse = {
  status: "ok" | "degraded";
  service: string;
  version: string;
  database: string;
};

export default function StatusDashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  useEffect(() => {
    // The URL comes from .env via NEXT_PUBLIC_ prefix, which Next.js
    // exposes to the browser. Default keeps things working if it's unset.
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    async function checkHealth() {
      try {
        const res = await fetch(`${apiUrl}/health`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: HealthResponse = await res.json();
        setHealth(data);
        setError(null);
      } catch (e) {
        // Most common cause: API container isn't running yet. The error
        // shows in the UI rather than silently failing.
        setError(e instanceof Error ? e.message : "Unknown error");
        setHealth(null);
      } finally {
        setLastChecked(new Date());
      }
    }

    // Initial check on mount, then poll every 10 seconds
    checkHealth();
    const interval = setInterval(checkHealth, 10_000);
    return () => clearInterval(interval);
  }, []);

  const isHealthy = health?.status === "ok";

  return (
    <section id="architecture" className="border-t border-ink-700/50 py-24 sm:py-32">
      <div className="mx-auto max-w-5xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-wider text-brand-400">
            Live system status
          </p>
          <h2 className="mt-3 text-4xl font-bold tracking-tight text-ink-100 sm:text-5xl">
            Architecture in motion
          </h2>
          <p className="mt-6 text-lg text-ink-300">
            The dashboard you&apos;re reading is pinging the live API every 10 seconds.
            This is the real backend, running in Docker, on the same machine.
          </p>
        </div>

        {/* Status card — different styling for healthy vs error states */}
        <div className="mt-12 overflow-hidden rounded-2xl border border-ink-700 bg-ink-800/50 backdrop-blur">
          <div className="border-b border-ink-700 bg-ink-800/80 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-medium text-ink-200">
                <Activity className="h-4 w-4" />
                System status
              </div>
              {/* Last-checked timestamp — small detail, builds trust */}
              {lastChecked && (
                <div className="text-xs font-mono text-ink-400">
                  Last checked {lastChecked.toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 divide-ink-700 sm:grid-cols-3 sm:divide-x">
            <StatusTile
              label="API"
              value={error ? "Unreachable" : isHealthy ? "Healthy" : "Degraded"}
              healthy={!error && isHealthy}
              icon={error || !isHealthy ? AlertCircle : CheckCircle2}
            />
            <StatusTile
              label="Database"
              value={health?.database || "—"}
              healthy={health?.database === "ok"}
              icon={Database}
            />
            <StatusTile
              label="Version"
              value={health?.version || "—"}
              healthy={!!health}
              icon={Activity}
              mono
            />
          </div>

          {error && (
            <div className="border-t border-ink-700 bg-red-500/5 px-6 py-4 text-sm text-red-300">
              <strong className="font-semibold">API unreachable:</strong> {error}.{" "}
              Make sure <code className="font-mono text-xs">docker compose up</code> is running.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

// Small subcomponent — kept in the same file because it's only used here.
// If it ever gets reused elsewhere, lift it into components/StatusTile.tsx.
function StatusTile({
  label,
  value,
  healthy,
  icon: Icon,
  mono,
}: {
  label: string;
  value: string;
  healthy: boolean;
  icon: React.ComponentType<{ className?: string }>;
  mono?: boolean;
}) {
  return (
    <div className="px-6 py-5">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-ink-400">
        <Icon className={`h-3.5 w-3.5 ${healthy ? "text-emerald-400" : "text-red-400"}`} />
        {label}
      </div>
      <div className={`mt-2 text-lg font-semibold ${mono ? "font-mono text-base" : ""} ${healthy ? "text-ink-100" : "text-red-300"}`}>
        {value}
      </div>
    </div>
  );
}