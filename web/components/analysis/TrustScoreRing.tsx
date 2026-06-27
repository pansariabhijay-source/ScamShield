"use client";

import { useEffect } from "react";
import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import type { VerdictTone } from "@/lib/types";
import { VERDICT } from "@/lib/verdict";

/**
 * Circular trust score. The arc sweeps into position and the integer counts
 * up in lockstep — the verdict literally "draws itself".
 */
export function TrustScoreRing({
  score,
  tone,
  label,
}: {
  score: number; // 0..100 scam probability
  tone: VerdictTone;
  label: string;
}) {
  const v = VERDICT[tone];
  const R = 86;
  const C = 2 * Math.PI * R;

  const progress = useMotionValue(0);
  const display = useTransform(progress, (p) => Math.round(p));
  const dash = useTransform(progress, (p) => C - (p / 100) * C);

  useEffect(() => {
    const controls = animate(progress, score, {
      duration: 1.5,
      ease: [0.22, 1, 0.36, 1],
      delay: 0.15,
    });
    return controls.stop;
  }, [score, progress]);

  return (
    <div className="relative grid place-items-center">
      {/* Soft tonal halo behind the ring */}
      <div
        className="pointer-events-none absolute h-56 w-56 rounded-full blur-2xl"
        style={{ background: v.soft }}
      />
      <svg width="216" height="216" viewBox="0 0 216 216" className="-rotate-90">
        <circle cx="108" cy="108" r={R} fill="none" stroke={v.ringTrack} strokeWidth="14" />
        <motion.circle
          cx="108"
          cy="108"
          r={R}
          fill="none"
          stroke={v.ring}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={C}
          style={{ strokeDashoffset: dash }}
        />
      </svg>

      <div className="absolute flex flex-col items-center">
        <div className="flex items-baseline">
          <motion.span className="text-[58px] font-semibold leading-none tracking-tight text-ink">
            {display}
          </motion.span>
          <span className="ml-1 text-2xl font-medium text-ink-faint">%</span>
        </div>
        <motion.span
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.5 }}
          className="mt-1 text-[15px] font-semibold"
          style={{ color: v.ring }}
        >
          {label}
        </motion.span>
      </div>
    </div>
  );
}
