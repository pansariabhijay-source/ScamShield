import type { DetectionResult, InputType } from "./types";
import { mockAnalyze } from "./mock";

/**
 * API layer. By default the app runs in DEMO mode (curated mock verdicts) so it
 * is instantly playable with no backend. Set NEXT_PUBLIC_LIVE_API=1 to call the
 * real FastAPI `/api/v1/detect/text` endpoint (proxied via next.config rewrites).
 */
const LIVE = process.env.NEXT_PUBLIC_LIVE_API === "1";

function fakeLatency() {
  return new Promise((r) => setTimeout(r, 1100 + Math.random() * 700));
}

export async function analyzeText(
  content: string,
  inputType: InputType = "TEXT",
): Promise<DetectionResult> {
  if (!LIVE) {
    await fakeLatency();
    return mockAnalyze(content, inputType);
  }
  const res = await fetch("/api/v1/detect/text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, input_type: inputType }),
  });
  if (!res.ok) throw new Error(`Analysis failed (${res.status})`);
  return (await res.json()) as DetectionResult;
}
