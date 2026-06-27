import type { StatsOverview, VerdictTone } from "./types";

/** Fetch real aggregate metrics from the FastAPI `/stats/overview` endpoint. */
export async function fetchStats(): Promise<StatsOverview> {
  const res = await fetch("/api/v1/stats/overview", {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`stats ${res.status}`);
  return (await res.json()) as StatsOverview;
}

/** Map a scam category label to a verdict tone for coloring. */
export function toneForCategory(category: string): VerdictTone {
  const c = category.toLowerCase();
  if (/(kyc|upi|fraud|phish|investment|otp|sextortion)/.test(c)) return "scam";
  if (/(job|courier|lottery|loan|romance)/.test(c)) return "warn";
  return "warn";
}
