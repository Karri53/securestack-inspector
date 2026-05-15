// frontend/components/ScanStatusPill.tsx
// Visual representation of a scan's status. One source of truth for the
// color/icon mapping - every place that shows a status uses this.

import { CheckCircle2, Clock, Loader2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ScanStatus } from "@/lib/types";

// Status → visual style mapping. Tailwind classes inline since each pill
// is tiny and a separate stylesheet would be over-engineering.
const STYLES: Record<ScanStatus, { bg: string; text: string; icon: typeof Clock }> = {
  pending: {
    bg: "bg-ink-700 border-ink-600",
    text: "text-ink-300",
    icon: Clock,
  },
  running: {
    // The brand color + pulse animation telegraph "work in progress"
    bg: "bg-brand-500/15 border-brand-500/40",
    text: "text-brand-400",
    icon: Loader2,
  },
  completed: {
    bg: "bg-emerald-500/15 border-emerald-500/40",
    text: "text-emerald-400",
    icon: CheckCircle2,
  },
  failed: {
    bg: "bg-red-500/15 border-red-500/40",
    text: "text-red-400",
    icon: XCircle,
  },
};

export default function ScanStatusPill({ status }: { status: ScanStatus }) {
  const style = STYLES[status];
  const Icon = style.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        style.bg,
        style.text,
      )}
    >
      <Icon
        className={cn("h-3 w-3", status === "running" && "animate-spin")}
        strokeWidth={2.5}
      />
      {status}
    </span>
  );
}