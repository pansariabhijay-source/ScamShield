"use client";

import { motion } from "framer-motion";
import { ScanLine, BrainCircuit, MessageCircleHeart } from "lucide-react";
import { SectionHeading } from "./SectionHeading";
import { Card } from "@/components/ui/card";

const STEPS = [
  {
    icon: ScanLine,
    title: "Share what’s suspicious",
    body: "Paste a text, drop a screenshot, or point your camera at a QR code. No setup, no jargon.",
  },
  {
    icon: BrainCircuit,
    title: "AI reads it like an expert",
    body: "Multiple detectors weigh urgency, impersonation, links and intent, then agree on a verdict.",
  },
  {
    icon: MessageCircleHeart,
    title: "Get a clear answer",
    body: "A trust score, the reasons behind it, and the single thing you should do next.",
  },
];

export function HowItWorks() {
  return (
    <section id="how" className="px-5 py-24">
      <div className="mx-auto max-w-6xl">
        <SectionHeading
          eyebrow="How it works"
          title="From “is this real?” to a clear answer in seconds"
          subtitle="ScamShield does the worrying for you, so a moment of doubt never turns into a costly mistake."
        />
        <div className="mt-14 grid gap-5 md:grid-cols-3">
          {STEPS.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 26 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.6, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
            >
              <Card className="h-full px-7 py-8">
                <div className="flex items-center gap-3">
                  <span className="grid h-11 w-11 place-items-center rounded-2xl bg-trust-50 text-trust-600">
                    <s.icon className="h-[22px] w-[22px]" strokeWidth={1.9} />
                  </span>
                  <span className="text-[13px] font-semibold text-ink-faint">0{i + 1}</span>
                </div>
                <h3 className="mt-5 text-[19px] font-semibold tracking-tight text-ink">{s.title}</h3>
                <p className="mt-2.5 text-[15px] leading-relaxed text-ink-soft">{s.body}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
