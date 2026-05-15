// frontend/components/ScanForm.tsx
// The submit-a-scan form. Single text input, single button.
//
// State machine here is intentionally simple:
//   idle -> submitting -> (success | error) -> idle
// More complex flows (multi-step, async URL validation, etc.) can come
// later; for now this is exactly what's needed.

"use client";

import { useState } from "react";
import { ArrowRight, Loader2 } from "lucide-react";
import { ApiError, submitScan } from "@/lib/api";

interface ScanFormProps {
  // Called after a successful submit so the parent can refresh its scans list
  onSuccess: () => void;
}

export default function ScanForm({ onSuccess }: ScanFormProps) {
  const [repoUrl, setRepoUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await submitScan(repoUrl.trim());
      setRepoUrl("");        // Clear input on success
      onSuccess();           // Tell parent to refresh
    } catch (err) {
      // ApiError messages from the backend are already user-friendly
      // (Pydantic produces things like "Only github.com URLs are supported")
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Could not reach the API. Is the backend running?");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-ink-700 bg-ink-800/50 p-6 backdrop-blur"
    >
      <label htmlFor="repo-url" className="block text-sm font-medium text-ink-200">
        GitHub repository URL
      </label>
      <p className="mt-1 text-xs text-ink-400">
        Paste a public github.com URL. The scan will clone the repo, parse its
        dependency manifests, and persist findings.
      </p>

      <div className="mt-4 flex flex-col gap-3 sm:flex-row">
        <input
          id="repo-url"
          type="url"
          required
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/expressjs/express"
          disabled={submitting}
          className="flex-1 rounded-lg border border-ink-700 bg-ink-900/80 px-4 py-2.5 text-sm text-ink-100 placeholder:text-ink-500 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30 disabled:cursor-not-allowed disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={submitting || !repoUrl.trim()}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 px-5 py-2.5 text-sm font-semibold text-ink-900 shadow-lg shadow-brand-500/25 transition-all hover:shadow-xl hover:shadow-brand-500/40 disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
        >
          {submitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Submitting
            </>
          ) : (
            <>
              Run scan
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </div>

      {/* Error message slot. Conditionally rendered so it doesn't take space when empty. */}
      {error && (
        <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2.5 text-sm text-red-300">
          {error}
        </div>
      )}
    </form>
  );
}