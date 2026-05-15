// frontend/lib/types.ts
// Mirrors the Pydantic schemas in backend/app/schemas/.
// When the backend contract changes, this is the first place to update.

export type ScanStatus = "pending" | "running" | "completed" | "failed";

export interface Scan {
  id: string;
  repo_url: string;
  status: ScanStatus;
  error_message: string | null;
  created_at: string;  // ISO timestamp
  updated_at: string;
}

export type FindingType = "dependency" | "dockerfile" | "sbom" | "vulnerability";
export type Severity = "info" | "low" | "medium" | "high" | "critical";

export interface Finding {
  id: string;
  scan_id: string;
  finding_type: FindingType;
  severity: Severity;
  package_name: string | null;
  package_version: string | null;
  package_ecosystem: string | null;
  manifest_path: string | null;
  message: string;
  extra_data: Record<string, unknown> | null;
  created_at: string;
}