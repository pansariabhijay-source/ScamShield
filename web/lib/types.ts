/**
 * Frontend mirror of the FastAPI `app/schemas/detection.py` contract.
 * Kept in sync with the backend so the UI can swap mock data for live calls
 * with zero shape changes.
 */

export type RiskLevel = "SAFE" | "SUSPICIOUS" | "HIGH_RISK" | "SCAM";

export type InputType =
  | "TEXT"
  | "SMS"
  | "EMAIL"
  | "WHATSAPP"
  | "URL"
  | "IMAGE"
  | "UPI"
  | "QR";

export type ScanStatus = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";

export interface RiskFactor {
  detector: string;
  code: string;
  description: string;
  weight: number;
}

export interface EngineScore {
  detector: string;
  score: number;
  confidence: number;
  explanation?: string | null;
}

export interface DetectionResult {
  scan_id: string;
  status: ScanStatus;
  input_type: InputType;
  scam_probability: number; // 0..100
  risk_level: RiskLevel;
  confidence: number; // 0..1
  category?: string | null;
  reasons: string[];
  recommendation?: string | null;
  risk_factors: RiskFactor[];
  engine_scores: EngineScore[];
  extracted_text?: string | null;
  model_version: string;
  created_at: string;
  /** UI-only: a plain-language explanation ("Explain like a human"). */
  human_summary?: string;
}

/** Mirror of the backend `app/schemas/stats.py` StatsOverview. */
export interface StatsTrendPoint {
  label: string;
  count: number;
}
export interface StatsCategory {
  category: string;
  count: number;
}
export interface StatsOverview {
  total_this_week: number;
  pct_change: number;
  trend: StatsTrendPoint[];
  categories: StatsCategory[];
  generated_at: string;
}

export interface ScanSummary {
  id: string;
  input_type: InputType;
  status: ScanStatus;
  risk_level: RiskLevel | null;
  scam_probability: number | null;
  category: string | null;
  created_at: string;
}

/** Maps a 0..100 scam probability to a verdict bucket + palette. */
export type VerdictTone = "safe" | "warn" | "scam";

export function toneForRisk(level: RiskLevel): VerdictTone {
  if (level === "SAFE") return "safe";
  if (level === "SUSPICIOUS") return "warn";
  return "scam"; // HIGH_RISK + SCAM
}

export function verdictLabel(level: RiskLevel): string {
  switch (level) {
    case "SAFE":
      return "Looks safe";
    case "SUSPICIOUS":
      return "Be careful";
    case "HIGH_RISK":
      return "High risk";
    case "SCAM":
      return "Likely a scam";
  }
}
