"use client";

import { motion } from "framer-motion";
import { Eyebrow } from "@/components/ui/card";

export function SectionHeading({
  eyebrow,
  title,
  subtitle,
  align = "center",
}: {
  eyebrow: string;
  title: React.ReactNode;
  subtitle?: string;
  align?: "center" | "left";
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 22 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className={align === "center" ? "mx-auto max-w-2xl text-center" : "max-w-2xl"}
    >
      <Eyebrow className="text-trust-500">{eyebrow}</Eyebrow>
      <h2 className="mt-4 text-balance text-[clamp(1.9rem,4vw,2.9rem)] font-semibold leading-tight tracking-[-0.025em] text-ink">
        {title}
      </h2>
      {subtitle && (
        <p className="mt-4 text-pretty text-[17px] leading-relaxed text-ink-soft">{subtitle}</p>
      )}
    </motion.div>
  );
}
