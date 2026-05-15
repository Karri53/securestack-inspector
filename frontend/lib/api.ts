// frontend/lib/api.ts
// Thin wrapper around fetch for talking to the SecureStack API.
// Every page that talks to the backend goes through this file.

import type { Finding, Scan } from "./types";

// In Docker, the browser hits localhost:8000 because the API exposes that port
// on the host. The NEXT_PUBLIC_ prefix is what makes env vars available in
// browser-side code (Next.js convention).
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Thrown when the API returns a non-2xx status. Components catch this
 * to render error states.
 */
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Internal helper. All other functions in this file go through here so
 * error handling, headers, and JSON parsing are consistent.
 */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
  const body = await response.json().catch(() => null);

  // FastAPI returns errors in two shapes:
  //   - Custom HTTPException: { detail: "Scan foo not found" }  (string)
  //   - Pydantic validation:  { detail: [ { msg, loc, ... }, ... ] }  (array)
  // Normalize both to a clean string for the UI.
  let message: string;
  if (Array.isArray(body?.detail)) {
    // Grab the first validation error's msg. Strip Pydantic's
    // "Value error, " prefix that custom validators add.
    const firstMsg = body.detail[0]?.msg ?? "Validation failed";
    message = firstMsg.replace(/^Value error,\s*/i, "");
  } else if (typeof body?.detail === "string") {
    message = body.detail;
  } else {
    message = response.statusText || "Request failed";
  }

  throw new ApiError(response.status, message);
}

  return response.json();
}

// ---- Public API surface ----
// One function per endpoint. Components import and call these directly.

export function submitScan(repo_url: string): Promise<Scan> {
  return request<Scan>("/api/scans", {
    method: "POST",
    body: JSON.stringify({ repo_url }),
  });
}

export function listScans(limit = 50): Promise<Scan[]> {
  return request<Scan[]>(`/api/scans?limit=${limit}`);
}

export function getScan(id: string): Promise<Scan> {
  return request<Scan>(`/api/scans/${id}`);
}

export function getFindings(scanId: string): Promise<Finding[]> {
  return request<Finding[]>(`/api/scans/${scanId}/findings`);
}