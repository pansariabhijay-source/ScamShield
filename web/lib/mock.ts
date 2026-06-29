import type { DetectionResult, InputType, ScanSummary, StatsOverview } from "./types";

/**
 * Demo intelligence. The product is fully interactive without a backend:
 * we keyword-match the input to one of three curated verdicts so the magic
 * is visible the instant someone lands from Product Hunt.
 */

const SCAM_KYC: DetectionResult = {
  scan_id: "demo-kyc",
  status: "COMPLETED",
  input_type: "WHATSAPP",
  scam_probability: 96,
  risk_level: "SCAM",
  confidence: 0.94,
  category: "KYC Scam",
  reasons: [
    "Uses urgency tactics to force a quick decision",
    "Requests sensitive information (OTP / PIN / KYC)",
    "Impersonates SBI / a trusted bank",
    "Contains a suspicious shortened domain",
  ],
  recommendation:
    "Delete this message. Do not click the link or share any details. Block the sender and report to 1930.",
  human_summary:
    "This message tries to create panic so you act before you think. Real banks never ask you to update KYC through a WhatsApp link. They’d ask you to visit a branch or the official app.",
  risk_factors: [
    { detector: "text.urgency", code: "URGENCY", description: "Urgency / deadline pressure", weight: 0.28 },
    { detector: "text.credential", code: "CREDENTIAL_REQUEST", description: "Asks for OTP / PIN / KYC", weight: 0.31 },
    { detector: "text.brand", code: "BRAND_IMPERSONATION", description: "Impersonates SBI", weight: 0.22 },
    { detector: "url.shortener", code: "SHORT_URL", description: "Shortened link hides destination", weight: 0.19 },
  ],
  engine_scores: [
    { detector: "Language model", score: 0.95, confidence: 0.93 },
    { detector: "URL reputation", score: 0.91, confidence: 0.88 },
    { detector: "Brand match", score: 0.97, confidence: 0.9 },
  ],
  model_version: "mvp-0.1.0",
  created_at: new Date().toISOString(),
};

const SUSPICIOUS_JOB: DetectionResult = {
  scan_id: "demo-job",
  status: "COMPLETED",
  input_type: "TEXT",
  scam_probability: 72,
  risk_level: "SUSPICIOUS",
  confidence: 0.79,
  category: "Job Scam",
  reasons: [
    "Promises unusually high pay for little work",
    "Asks for an upfront registration fee",
    "Contact is over WhatsApp only, no company domain",
  ],
  recommendation:
    "Don’t pay any fee. Verify the company on its official website and never share bank details to ‘get hired’.",
  human_summary:
    "Legitimate employers don’t ask you to pay to get a job. ‘Work from home, ₹3,000/day’ offers that route you to a personal WhatsApp number are almost always after your money or your bank details.",
  risk_factors: [
    { detector: "text.payout", code: "TOO_GOOD", description: "Unrealistic earnings claim", weight: 0.26 },
    { detector: "text.fee", code: "UPFRONT_FEE", description: "Requests an upfront fee", weight: 0.3 },
    { detector: "text.channel", code: "OFF_CHANNEL", description: "WhatsApp-only contact", weight: 0.18 },
  ],
  engine_scores: [
    { detector: "Language model", score: 0.74, confidence: 0.8 },
    { detector: "Pattern rules", score: 0.69, confidence: 0.72 },
  ],
  model_version: "mvp-0.1.0",
  created_at: new Date().toISOString(),
};

const SAFE_OTP: DetectionResult = {
  scan_id: "demo-safe",
  status: "COMPLETED",
  input_type: "SMS",
  scam_probability: 12,
  risk_level: "SAFE",
  confidence: 0.86,
  category: "Likely legitimate",
  reasons: [
    "No links or attachments",
    "Matches a known transactional sender format",
    "Does not request any sensitive information",
  ],
  recommendation:
    "This looks like a normal transaction alert. Still, never share an OTP with anyone who calls you.",
  human_summary:
    "This reads like a routine alert from your bank. It isn’t asking you to click anything or hand over a code, which is a good sign. The only rule to remember: an OTP is never shared with a caller.",
  risk_factors: [
    { detector: "text.links", code: "NO_LINKS", description: "Contains no links", weight: 0.1 },
    { detector: "text.sender", code: "KNOWN_FORMAT", description: "Known transactional format", weight: 0.12 },
  ],
  engine_scores: [
    { detector: "Language model", score: 0.13, confidence: 0.85 },
    { detector: "Pattern rules", score: 0.1, confidence: 0.82 },
  ],
  model_version: "mvp-0.1.0",
  created_at: new Date().toISOString(),
};

const UPI_FRAUD: DetectionResult = {
  scan_id: "demo-upi",
  status: "COMPLETED",
  input_type: "UPI",
  scam_probability: 91,
  risk_level: "SCAM",
  confidence: 0.9,
  category: "UPI Fraud",
  reasons: [
    "This is a ‘collect’ request, so you’d be paying, not receiving",
    "Promises cashback or a refund to lower your guard",
    "Payee VPA is unverified and recently created",
  ],
  recommendation:
    "Do not approve this request. You never need to approve a UPI request to receive money. Decline it and block the sender.",
  human_summary:
    "Someone sent you a UPI ‘collect’ request dressed up as a reward. Approving it takes money OUT of your account. Receiving money never needs your PIN. Decline it.",
  risk_factors: [
    { detector: "upi.collect", code: "COLLECT_REQUEST", description: "Money-pull request", weight: 0.34 },
    { detector: "upi.reward", code: "FAKE_REWARD", description: "Cashback / refund lure", weight: 0.28 },
    { detector: "upi.vpa", code: "UNVERIFIED_VPA", description: "Unverified payee handle", weight: 0.21 },
  ],
  engine_scores: [
    { detector: "UPI heuristics", score: 0.93, confidence: 0.9 },
    { detector: "Language model", score: 0.88, confidence: 0.86 },
  ],
  model_version: "mvp-0.1.0",
  created_at: new Date().toISOString(),
};

const PAYMENT_LURE: DetectionResult = {
  scan_id: "demo-lure",
  status: "COMPLETED",
  input_type: "SMS",
  scam_probability: 87,
  risk_level: "SCAM",
  confidence: 0.9,
  category: "Payment / Phishing Link",
  reasons: [
    "Shortened link hides the real destination",
    "Fake ‘money received / cashback’ lure to make you click",
    "Pressure to ‘check now’ / act immediately",
    "Real UPI credits appear in your bank app — never via a link",
  ],
  recommendation:
    "Do not click the link. A genuine UPI credit shows up directly in your bank/UPI app and never needs you to tap a link to ‘claim’ or ‘check’ it. Delete and block the sender.",
  human_summary:
    "This dangles ‘₹ received, check now’ next to a shortened link. That combination is a classic phishing trap — the link leads to a fake page or a malware download, not your money. Money you actually receive shows up in your bank app on its own.",
  risk_factors: [
    { detector: "url.shortener", code: "SHORT_URL", description: "Shortened link hides destination", weight: 0.32 },
    { detector: "text.lure", code: "PAYMENT_LURE", description: "Fake ‘money received’ bait", weight: 0.28 },
    { detector: "text.urgency", code: "URGENCY", description: "‘Check now’ pressure", weight: 0.2 },
  ],
  engine_scores: [
    { detector: "Language model", score: 0.86, confidence: 0.9 },
    { detector: "URL reputation", score: 0.84, confidence: 0.88 },
  ],
  model_version: "mvp-0.1.0",
  created_at: new Date().toISOString(),
};

const stamp = (r: DetectionResult): DetectionResult => ({
  ...r,
  created_at: new Date().toISOString(),
});

// Link-based lures are scams regardless of friendly "received/credited" wording.
const SHORTENER = /\b(bit\.ly|tinyurl\.com|goo\.gl|t\.co|ow\.ly|is\.gd|cutt\.ly|rb\.gy|shorturl\.at|rebrand\.ly)\b/;
const HAS_LINK = /(https?:\/\/|www\.|\b[a-z0-9-]+\.(com|in|co|net|org|xyz|top|club|link|info|ly|gd|me)\b)/i;
const ACTION_LURE = /(check now|click|claim|verify|login|update|act now|tap here|open link)/;

/**
 * Pick a curated verdict from the input text. `inputType` biases the choice so
 * QR / UPI / screenshot modes resolve to sensible categories.
 */
export function mockAnalyze(input: string, inputType: InputType = "TEXT"): DetectionResult {
  const t = input.toLowerCase();

  const hasLink = HAS_LINK.test(t);
  const hasShortener = SHORTENER.test(t);

  // Highest priority: a shortened link, or any link paired with a "click/check
  // now / claim" call-to-action, is a phishing lure no matter how friendly the
  // wrapper text ("₹ received", "cashback") sounds. Catches the UPI/wallet
  // "money received → tap link" scam that naive keyword rules wave through.
  if (hasShortener || (hasLink && ACTION_LURE.test(t))) {
    return stamp(PAYMENT_LURE);
  }

  if (inputType === "UPI" || inputType === "QR" || /collect request|requested ₹|approve to receive|@ok|@ybl|@paytm|cashback/.test(t)) {
    return stamp({ ...UPI_FRAUD, input_type: inputType === "QR" ? "QR" : "UPI" });
  }
  if (/(job|hiring|work from home|earn|salary|part.?time|₹\s?\d{3,})/.test(t) && !/kyc|bank|otp/.test(t)) {
    return stamp(SUSPICIOUS_JOB);
  }
  // A transaction alert is only "safe" when it carries NO link and isn't urging
  // you to click/verify — otherwise it's a lure dressed up as a credit notice.
  if (
    /(otp|credited|debited|received|a\/c|balance|txn)/.test(t) &&
    !hasLink && !ACTION_LURE.test(t) &&
    !/kyc|expire|verify|suspend/.test(t)
  ) {
    return stamp(SAFE_OTP);
  }
  return stamp({ ...SCAM_KYC, input_type: inputType === "IMAGE" ? "IMAGE" : "WHATSAPP" });
}

// `when` is a fixed, pre-formatted relative label so SSR and client render
// identically (no Date.now() at render → no hydration mismatch).
export type RecentScan = ScanSummary & { when: string };

const FIXED_TS = "2026-06-28T00:00:00.000Z";

export const RECENT_SCANS: RecentScan[] = [
  { id: "s1", input_type: "WHATSAPP", status: "COMPLETED", risk_level: "SCAM", scam_probability: 96, category: "KYC Scam", created_at: FIXED_TS, when: "6m ago" },
  { id: "s2", input_type: "QR", status: "COMPLETED", risk_level: "HIGH_RISK", scam_probability: 88, category: "UPI Fraud", created_at: FIXED_TS, when: "34m ago" },
  { id: "s3", input_type: "URL", status: "COMPLETED", risk_level: "SUSPICIOUS", scam_probability: 64, category: "Courier Scam", created_at: FIXED_TS, when: "1h ago" },
  { id: "s4", input_type: "SMS", status: "COMPLETED", risk_level: "SAFE", scam_probability: 9, category: "Transaction alert", created_at: FIXED_TS, when: "3h ago" },
  { id: "s5", input_type: "EMAIL", status: "COMPLETED", risk_level: "SCAM", scam_probability: 93, category: "Investment Scam", created_at: FIXED_TS, when: "5h ago" },
];

// Fixed positions for the abstract activity field; zipped with whatever
// categories the stats payload returns (real or demo).
export const NODE_POSITIONS: { x: number; y: number }[] = [
  { x: 30, y: 58 },
  { x: 41, y: 27 },
  { x: 41, y: 76 },
  { x: 46, y: 66 },
  { x: 60, y: 40 },
  { x: 33, y: 38 },
  { x: 66, y: 70 },
  { x: 24, y: 72 },
];

/**
 * Demo fallback shaped exactly like the backend StatsOverview. Used when the
 * API is unreachable or the database is empty, so the section still looks alive.
 */
export const DEMO_STATS: StatsOverview = {
  total_this_week: 8932,
  pct_change: 18,
  generated_at: FIXED_TS,
  trend: [
    { label: "Mon", count: 820 },
    { label: "Tue", count: 932 },
    { label: "Wed", count: 901 },
    { label: "Thu", count: 1290 },
    { label: "Fri", count: 1490 },
    { label: "Sat", count: 1620 },
    { label: "Sun", count: 1380 },
  ],
  categories: [
    { category: "UPI Fraud", count: 1640 },
    { category: "KYC Scam", count: 1284 },
    { category: "Job Scam", count: 980 },
    { category: "Courier Scam", count: 742 },
    { category: "Investment Scam", count: 633 },
    { category: "Phishing", count: 588 },
  ],
};
