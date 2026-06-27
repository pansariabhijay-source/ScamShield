"use client";

import { motion } from "framer-motion";
import { ShieldCheck } from "lucide-react";
import { TrustInput } from "./TrustInput";
import { AnalysisPanel } from "@/components/analysis/AnalysisPanel";
import { ParticleField } from "@/components/shared/ParticleField";

const EASE = [0.22, 1, 0.36, 1] as const;

export function Hero() {
  return (
    <section id="top" className="aura relative overflow-hidden px-5 pb-10 pt-36 sm:pt-40">
      {/* Aether-Flow particle network — mouse-reactive, fades toward the content */}
      <ParticleField className="pointer-events-none absolute inset-0 h-full w-full opacity-70 [mask-image:radial-gradient(120%_90%_at_50%_0%,black_30%,transparent_85%)]" />
      {/* faint dotted grid, fading out toward the bottom */}
      <div className="grid-dots pointer-events-none absolute inset-0 [mask-image:linear-gradient(to_bottom,black,transparent_75%)]" />

      <div className="relative mx-auto max-w-3xl text-center">
        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.05, ease: EASE }}
          className="text-balance text-[clamp(2.75rem,7vw,4.75rem)] font-semibold leading-[0.98] tracking-[-0.03em] text-ink"
        >
          Can I trust <span className="text-gradient">this?</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.15, ease: EASE }}
          className="mx-auto mt-5 max-w-xl text-pretty text-[18px] leading-relaxed text-ink-soft"
        >
          Paste a message, upload a screenshot, or scan a QR code. ScamShield
          instantly tells you whether it&apos;s safe or a scam, and why.
        </motion.p>
      </div>

      <div className="relative mt-10">
        <TrustInput />
      </div>

      <div className="relative mx-auto mt-7 flex max-w-2xl flex-wrap items-center justify-center gap-x-6 gap-y-2 text-[13px] text-ink-faint">
        <span className="inline-flex items-center gap-1.5">
          <ShieldCheck className="h-4 w-4 text-trust-400" /> Bank-grade analysis
        </span>
        <span className="h-1 w-1 rounded-full bg-line" />
        <span>Results in under 2 seconds</span>
        <span className="h-1 w-1 rounded-full bg-line" />
        <span>No sign-up to try</span>
      </div>

      <AnalysisPanel />
    </section>
  );
}
