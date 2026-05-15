// frontend/app/dashboard/page.tsx
// The dashboard route. Composes the nav + scan form + scans list.
//
// State that lives here:
//   refreshKey - bumped whenever a scan is submitted, triggers an immediate
//                refetch in ScansList without waiting for the next poll tick.

"use client";

import { useState } from "react";
import DashboardNav from "@/components/DashboardNav";
import ScanForm from "@/components/ScanForm";
import ScansList from "@/components/ScansList";

export default function DashboardPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <>
      <DashboardNav />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-ink-100">
            Scan dashboard
          </h1>
          <p className="mt-2 text-sm text-ink-400">
            Submit a public GitHub repo to analyze its dependency manifests.
            Findings appear below as soon as the worker finishes.
          </p>
        </div>

        <div className="space-y-6">
          <ScanForm onSuccess={() => setRefreshKey((k) => k + 1)} />
          <ScansList refreshKey={refreshKey} />
        </div>
      </main>
    </>
  );
}