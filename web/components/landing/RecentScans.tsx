"use client";

import { motion } from "framer-motion";
import {
  MessageCircle,
  QrCode,
  Link2,
  Mail,
  Smartphone,
  ChevronRight,
} from "lucide-react";
import { SectionHeading } from "./SectionHeading";
import { Card } from "@/components/ui/card";
import { RECENT_SCANS } from "@/lib/mock";
import { toneForRisk, verdictLabel, type InputType } from "@/lib/types";
import { VERDICT } from "@/lib/verdict";
import { cn } from "@/lib/utils";

const ICONS: Record<InputType, typeof Link2> = {
  WHATSAPP: MessageCircle,
  TEXT: MessageCircle,
  SMS: Smartphone,
  QR: QrCode,
  URL: Link2,
  EMAIL: Mail,
  IMAGE: Link2,
  UPI: Smartphone,
};

const SOURCE_LABEL: Record<InputType, string> = {
  WHATSAPP: "WhatsApp message",
  TEXT: "Pasted message",
  SMS: "SMS",
  QR: "QR code",
  URL: "Link",
  EMAIL: "Email",
  IMAGE: "Screenshot",
  UPI: "UPI request",
};

export function RecentScans() {
  return (
    <section id="activity" className="px-5 py-24">
      <div className="mx-auto max-w-3xl">
        <SectionHeading
          eyebrow="Recent activity"
          title="Every check, beautifully logged"
          subtitle="A calm, scannable history, so you always know what was checked and what was caught."
        />

        <div className="mt-12 space-y-2.5">
          {RECENT_SCANS.map((scan, i) => {
            const tone = toneForRisk(scan.risk_level ?? "SAFE");
            const v = VERDICT[tone];
            const Icon = ICONS[scan.input_type];
            return (
              <motion.div
                key={scan.id}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.5, delay: i * 0.07, ease: [0.22, 1, 0.36, 1] }}
              >
                <Card className="group flex items-center gap-4 px-5 py-4 transition-all hover:-translate-y-0.5 hover:shadow-float">
                  <span className={cn("grid h-11 w-11 shrink-0 place-items-center rounded-2xl", v.chip)}>
                    <Icon className="h-5 w-5" strokeWidth={1.9} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="truncate text-[15px] font-semibold text-ink">
                        {SOURCE_LABEL[scan.input_type]} analyzed
                      </p>
                      <span className={cn("hidden rounded-full px-2 py-0.5 text-[11.5px] font-semibold sm:inline", v.chip)}>
                        {scan.category}
                      </span>
                    </div>
                    <p className="mt-0.5 text-[13px] text-ink-faint">
                      {verdictLabel(scan.risk_level ?? "SAFE")} · {scan.when}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-right">
                      <span className="block text-[18px] font-semibold leading-none" style={{ color: v.ring }}>
                        {scan.scam_probability}%
                      </span>
                      <span className="text-[11px] font-medium text-ink-faint">{v.label}</span>
                    </span>
                    <ChevronRight className="h-4 w-4 text-ink-faint transition-transform group-hover:translate-x-0.5" />
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
