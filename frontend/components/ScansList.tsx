// frontend/components/ScansList.tsx
// Live-updating list of recent scans.
//
// Polling strategy: only poll when there's actually work in progress.
// Idle dashboards make zero API calls. Once any scan is pending or running,
// we poll every 3s until all scans hit a terminal state.
//
// The `refreshKey` prop lets the parent force an immediate refetch when
// a new scan is submitted (don't wait for the next polling tick).

"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ExternalLink, Inbox } from "lucide-react";
import { ApiError, listScans } from "@/lib/api";
import type { Scan } from "@/lib/types";
import ScanStatusPill from "./ScanStatusPill";

const POLL_INTERVAL_MS = 3000;

interface ScansListProps {
  refreshKey: number;  // Bumping this triggers an immediate refetch
}

export default function ScansList({ refreshKey }: ScansListProps) {
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchScans = useCallback(async () => {
    try {
      const data = await listScans();
      setScans(data);
      setError(null);
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : "Could not reach the API";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load + refetch on refreshKey change (e.g. after form submit)
  useEffect(() => {
    fetchScans();
  }, [fetchScans, refreshKey]);

  // Polling: only when at least one scan is in-progress.
  // The dependency array includes `scans` so this re-runs whenever statuses
  // change, naturally winding the loop down once all scans complete.
  useEffect(() => {
    const hasInProgress = scans.some(
      (s) => s.status === "pending" || s.status === "running",
    );
    if (!hasInProgress) return;

    const id = setInterval(fetchScans, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [scans, fetchScans]);

  if (loading) {
    return (
      <div className="rounded-2xl border border-ink-700 bg-ink-800/30 p-12 text-center text-sm text-ink-400">
        Loading scans...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-sm text-red-300">
        <strong className="font-semibold">Failed to load scans:</strong> {error}
      </div>
    );
  }

  if (scans.length === 0) {
    return (
      <div className="rounded-2xl border border-ink-700 bg-ink-800/30 p-12 text-center">
        <Inbox className="mx-auto h-10 w-10 text-ink-500" />
        <p className="mt-4 text-sm font-medium text-ink-200">No scans yet</p>
        <p className="mt-1 text-xs text-ink-400">
          Submit a repo above to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-ink-700 bg-ink-800/30 backdrop-blur">
      <div className="border-b border-ink-700 bg-ink-800/50 px-6 py-3">
        <h2 className="text-sm font-semibold text-ink-200">Recent scans</h2>
      </div>
      <ul className="divide-y divide-ink-700">
        {scans.map((scan) => (
          <li key={scan.id}>
            <Link
              href={`/dashboard/scans/${scan.id}`}
              className="flex items-center gap-4 px-6 py-4 transition-colors hover:bg-ink-800/50"
            >
              <ScanStatusPill status={scan.status} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-ink-100">
                  {humanizeRepoUrl(scan.repo_url)}
                </p>
                <p className="mt-0.5 text-xs text-ink-400">
                  {formatRelativeTime(scan.created_at)}
                </p>
              </div>
              <ExternalLink className="h-4 w-4 flex-shrink-0 text-ink-500" />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ---- Local helpers ----
// Kept here rather than in lib/utils so they stay close to their only caller.

function humanizeRepoUrl(url: string): string {
  // "https://github.com/expressjs/express" -> "expressjs/express"
  return url.replace(/^https?:\/\/(www\.)?github\.com\//i, "");
}

function formatRelativeTime(iso: string): string {
  const then = new Date(iso).getTime();
  const now = Date.now();
  const diffSec = Math.floor((now - then) / 1000);

  if (diffSec < 60) return "just now";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
}