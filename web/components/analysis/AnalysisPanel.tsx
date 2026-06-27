"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  AlertTriangle,
  Ban,
  Check,
  Flag,
  Link2Off,
  ShieldCheck,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import { useAnalysis } from "@/store/useAnalysis";
import { toneForRisk, verdictLabel } from "@/lib/types";
import { VERDICT } from "@/lib/verdict";
import { TrustScoreRing } from "./TrustScoreRing";
import { Card, Eyebrow } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const EASE = [0.22, 1, 0.36, 1] as const;

/** Picks an action icon by matching the recommendation text. */
function actionIcon(text: string) {
  const t = text.toLowerCase();
  if (t.includes("delete")) return Trash2;
  if (t.includes("block")) return Ban;
  if (t.includes("report")) return Flag;
  if (t.includes("link")) return Link2Off;
  return ShieldCheck;
}

function deriveActions(rec: string): string[] {
  // Split a recommendation sentence into 1-tap chips.
  return rec
    .split(/[.•]|\sand\s/)
    .map((s) => s.trim())
    .filter((s) => s.length > 8)
    .slice(0, 4);
}

export function AnalysisPanel() {
  const { phase, result, reset } = useAnalysis();
  const open = phase === "analyzing" || phase === "done" || phase === "error";

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          key="analysis"
          initial={{ opacity: 0, y: 36 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.6, ease: EASE }}
          className="mx-auto mt-12 w-full max-w-5xl"
        >
          {phase === "analyzing" && <Thinking />}
          {phase === "error" && <ErrorState />}
          {phase === "done" && result && <Result />}

          {phase === "done" && (
            <div className="mt-6 flex justify-center">
              <Button variant="ghost" onClick={reset}>
                <X className="h-4 w-4" /> Analyze something else
              </Button>
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function Thinking() {
  const steps = ["Reading the message", "Checking links & senders", "Weighing the evidence"];
  return (
    <Card className="grid place-items-center gap-5 px-8 py-16">
      <div className="relative grid h-16 w-16 place-items-center">
        <span className="absolute h-16 w-16 rounded-full border-2 border-trust-500/25" />
        <motion.span
          className="absolute h-16 w-16 rounded-full border-2 border-transparent border-t-trust-500"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
        />
        <Sparkles className="h-6 w-6 text-trust-500" />
      </div>
      <div className="space-y-1 text-center">
        {steps.map((s, i) => (
          <motion.p
            key={s}
            initial={{ opacity: 0.25 }}
            animate={{ opacity: [0.25, 1, 0.25] }}
            transition={{ duration: 1.8, repeat: Infinity, delay: i * 0.45 }}
            className="text-[15px] font-medium text-ink-soft"
          >
            {s}
          </motion.p>
        ))}
      </div>
    </Card>
  );
}

function ErrorState() {
  const { error, reset } = useAnalysis();
  return (
    <Card className="flex flex-col items-center gap-4 px-8 py-14 text-center">
      <AlertTriangle className="h-8 w-8 text-warn-500" />
      <p className="text-ink-soft">{error ?? "Something went wrong."}</p>
      <Button variant="secondary" onClick={reset}>
        Try again
      </Button>
    </Card>
  );
}

function Result() {
  const result = useAnalysis((s) => s.result)!;
  const tone = toneForRisk(result.risk_level);
  const v = VERDICT[tone];
  const actions = result.recommendation ? deriveActions(result.recommendation) : [];

  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_1.25fr]">
      {/* LEFT — verdict + category + actions */}
      <div className="flex flex-col gap-5">
        <Card className="flex flex-col items-center gap-6 px-7 py-9">
          <div className="flex w-full items-center justify-between">
            <Eyebrow>Trust verdict</Eyebrow>
            <span className={cn("rounded-full px-2.5 py-1 text-[12px] font-semibold", v.chip)}>
              {Math.round(result.confidence * 100)}% confident
            </span>
          </div>
          <TrustScoreRing score={result.scam_probability} tone={tone} label={verdictLabel(result.risk_level)} />

          {result.category && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.25, duration: 0.5 }}
              className={cn("w-full rounded-2xl px-4 py-3 text-center", v.bg)}
            >
              <p className="text-[12px] font-medium uppercase tracking-wider text-ink-faint">Category</p>
              <p className={cn("text-[17px] font-semibold", v.text)}>{result.category}</p>
            </motion.div>
          )}
        </Card>

        {/* Recommended action */}
        <Card className="px-6 py-6">
          <Eyebrow>What you should do</Eyebrow>
          <div className="mt-4 flex flex-col gap-2.5">
            {actions.map((a, i) => {
              const Icon = actionIcon(a);
              return (
                <motion.button
                  key={a}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.4 + i * 0.12, duration: 0.5, ease: EASE }}
                  className="group flex items-center gap-3 rounded-2xl border border-line bg-offwhite px-4 py-3 text-left transition-all hover:border-trust-200 hover:bg-trust-50"
                >
                  <span className={cn("grid h-9 w-9 shrink-0 place-items-center rounded-xl", v.chip)}>
                    <Icon className="h-[18px] w-[18px]" strokeWidth={2} />
                  </span>
                  <span className="text-[14.5px] font-medium text-ink">{a}</span>
                </motion.button>
              );
            })}
          </div>
        </Card>
      </div>

      {/* RIGHT — reasoning + human explanation */}
      <div className="flex flex-col gap-5">
        <Card className="px-7 py-7">
          <Eyebrow>Why ScamShield thinks this</Eyebrow>
          <div className="mt-5 grid gap-2.5 sm:grid-cols-2">
            {result.reasons.map((r, i) => (
              <motion.div
                key={r}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + i * 0.13, duration: 0.5, ease: EASE }}
                className="flex items-start gap-2.5 rounded-2xl border border-white/[0.06] bg-white/[0.03] px-4 py-3.5 shadow-soft"
              >
                <span className={cn("mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full", v.chip)}>
                  <Check className="h-3 w-3" strokeWidth={3} />
                </span>
                <span className="text-[14px] leading-snug text-ink-soft">{r}</span>
              </motion.div>
            ))}
          </div>
        </Card>

        {result.human_summary && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.05, duration: 0.6, ease: EASE }}
          >
            <Card className="relative overflow-hidden px-7 py-7">
              <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-trust-50 blur-2xl" />
              <Eyebrow className="text-trust-600">
                <Sparkles className="h-3.5 w-3.5" /> Explain like a human
              </Eyebrow>
              <p className="mt-4 text-[18px] font-medium leading-relaxed tracking-tight text-ink">
                {result.human_summary}
              </p>
            </Card>
          </motion.div>
        )}

        {/* Engine consensus — quiet credibility */}
        <Card className="px-7 py-6">
          <Eyebrow>Engine consensus</Eyebrow>
          <div className="mt-4 space-y-3.5">
            {result.engine_scores.map((e, i) => (
              <div key={e.detector} className="flex items-center gap-3">
                <span className="w-32 shrink-0 text-[13px] text-ink-soft">{e.detector}</span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-card">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.round(e.score * 100)}%` }}
                    transition={{ delay: 0.7 + i * 0.15, duration: 0.9, ease: EASE }}
                    className="h-full rounded-full"
                    style={{ background: v.ring }}
                  />
                </div>
                <span className="w-9 text-right text-[13px] font-medium text-ink-faint">
                  {Math.round(e.score * 100)}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
