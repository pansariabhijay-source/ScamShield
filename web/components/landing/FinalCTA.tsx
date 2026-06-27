"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { focusAnalyzer } from "@/lib/focus";

export function FinalCTA() {
  return (
    <section className="px-5 py-20">
      <motion.div
        initial={{ opacity: 0, y: 28 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="relative mx-auto max-w-5xl overflow-hidden rounded-[32px] border border-white/[0.08] px-8 py-16 text-center shadow-float"
        style={{ background: "linear-gradient(180deg,#140f24 0%,#0b0816 100%)" }}
      >
        <div className="pointer-events-none absolute -top-24 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-[radial-gradient(circle,rgba(59,108,246,0.18),transparent_70%)] blur-2xl" />
        <h2 className="relative text-balance text-[clamp(2rem,4.5vw,3.2rem)] font-semibold leading-tight tracking-[-0.03em] text-ink">
          Never wonder <span className="text-gradient">“is this safe?”</span> again.
        </h2>
        <p className="relative mx-auto mt-5 max-w-xl text-[17px] leading-relaxed text-ink-soft">
          Join thousands who check before they click. Free to start, for you and the people you love.
        </p>
        <div className="relative mt-9 flex flex-wrap items-center justify-center gap-3">
          <Button size="lg" onClick={focusAnalyzer}>
            Analyze something now <ArrowRight className="h-4 w-4" />
          </Button>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => document.getElementById("how")?.scrollIntoView({ behavior: "smooth" })}
          >
            See how it works
          </Button>
        </div>
      </motion.div>
    </section>
  );
}
