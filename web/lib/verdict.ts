import type { VerdictTone } from "./types";

/** Centralized verdict palette so risk color appears consistently — and rarely. */
export const VERDICT = {
  safe: {
    ring: "#34d399",
    ringTrack: "#10322a",
    text: "text-safe-600",
    bg: "bg-safe-50",
    chip: "bg-safe-50 text-safe-600",
    soft: "rgba(16,185,129,0.12)",
    label: "Safe",
  },
  warn: {
    ring: "#fbbf24",
    ringTrack: "#33280f",
    text: "text-warn-600",
    bg: "bg-warn-50",
    chip: "bg-warn-50 text-warn-600",
    soft: "rgba(245,158,11,0.12)",
    label: "Suspicious",
  },
  scam: {
    ring: "#f87176",
    ringTrack: "#331a1e",
    text: "text-scam-600",
    bg: "bg-scam-50",
    chip: "bg-scam-50 text-scam-600",
    soft: "rgba(241,100,108,0.12)",
    label: "Scam",
  },
} as const satisfies Record<VerdictTone, unknown>;

export type VerdictStyle = (typeof VERDICT)[VerdictTone];
