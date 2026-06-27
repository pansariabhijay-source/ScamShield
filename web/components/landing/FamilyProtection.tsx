"use client";

import { motion } from "framer-motion";
import { Forward, Users, BellRing, ShieldCheck, Heart } from "lucide-react";
import { SectionHeading } from "./SectionHeading";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { focusAnalyzer } from "@/lib/focus";

const FEATURES = [
  {
    icon: Forward,
    title: "Forward & we’ll check",
    body: "Mom forwards a suspicious WhatsApp message. ScamShield replies in seconds with a simple verdict she can trust.",
  },
  {
    icon: Users,
    title: "One shared dashboard",
    body: "See what your family has scanned and what was blocked, without ever reading their private messages.",
  },
  {
    icon: BellRing,
    title: "Gentle alerts that matter",
    body: "If a parent is targeted by a high-risk scam, you get a calm heads-up so you can call before they tap.",
  },
];

export function FamilyProtection() {
  return (
    <section id="family" className="px-5 py-24">
      <div className="mx-auto max-w-6xl">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          {/* Left — emotional copy + features */}
          <div>
            <SectionHeading
              align="left"
              eyebrow="Family protection"
              title={
                <>
                  Protect your parents
                  <br />
                  online.
                </>
              }
              subtitle="The people we love most are targeted most. ScamShield quietly stands between them and the scam. No tech skills required."
            />
            <div className="mt-9 space-y-3">
              {FEATURES.map((f, i) => (
                <motion.div
                  key={f.title}
                  initial={{ opacity: 0, x: -18 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-60px" }}
                  transition={{ duration: 0.55, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
                  className="flex items-start gap-4 rounded-2xl border border-white/[0.06] bg-card/60 px-5 py-4 shadow-soft"
                >
                  <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-trust-50 text-trust-600">
                    <f.icon className="h-5 w-5" strokeWidth={1.9} />
                  </span>
                  <div>
                    <h3 className="text-[15.5px] font-semibold text-ink">{f.title}</h3>
                    <p className="mt-1 text-[14px] leading-relaxed text-ink-soft">{f.body}</p>
                  </div>
                </motion.div>
              ))}
            </div>
            <Button size="lg" className="mt-8" onClick={focusAnalyzer}>
              <Heart className="h-4 w-4" /> Try it with a message
            </Button>
          </div>

          {/* Right — chat mockup */}
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.97 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="relative"
          >
            <div className="pointer-events-none absolute -inset-6 -z-10 rounded-[40px] bg-[radial-gradient(60%_50%_at_60%_30%,rgba(59,108,246,0.14),transparent_70%)] blur-2xl" />
            <Card className="mx-auto max-w-sm overflow-hidden p-0">
              <div className="flex items-center gap-3 border-b border-line px-5 py-4">
                <span className="grid h-9 w-9 place-items-center rounded-full bg-safe-100 text-safe-600 text-[15px] font-semibold">
                  M
                </span>
                <div className="leading-tight">
                  <p className="text-[14.5px] font-semibold text-ink">Mom</p>
                  <p className="text-[12px] text-safe-600">Protected by ScamShield</p>
                </div>
              </div>
              <div className="space-y-3 bg-offwhite px-5 py-6">
                <div className="ml-auto max-w-[80%] rounded-2xl rounded-tr-md bg-white/[0.08] px-4 py-3 text-[13.5px] text-ink-soft shadow-soft">
                  “Your electricity will be disconnected tonight. Pay now: bit.ly/pay-bill”
                </div>
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                  className="max-w-[88%] rounded-2xl rounded-tl-md border border-scam-100 bg-scam-50 px-4 py-3.5"
                >
                  <div className="flex items-center gap-2 text-scam-600">
                    <ShieldCheck className="h-4 w-4" />
                    <span className="text-[13px] font-semibold">96% likely a scam</span>
                  </div>
                  <p className="mt-1.5 text-[13px] leading-relaxed text-ink-soft">
                    This is an electricity-bill scam. Don’t pay or tap the link. Your board never asks for instant
                    payment over WhatsApp. Want me to block this number?
                  </p>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.9 }}
                  className="flex items-center justify-center gap-1.5 pt-1 text-[12px] font-medium text-ink-faint"
                >
                  <BellRing className="h-3.5 w-3.5 text-trust-400" /> Aarav was notified
                </motion.div>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
