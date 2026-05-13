// frontend/lib/utils.ts
// `cn()` is shadcn/ui's classic helper for combining Tailwind classes
// without conflicts. clsx handles conditional logic, tailwind-merge
// resolves "px-4 px-6" → "px-6" instead of leaving both in the output.

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}