"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Logo } from "@/components/shared/Logo";
import { Button } from "@/components/ui/button";
import { focusAnalyzer } from "@/lib/focus";

const LINKS = [
  { label: "How it works", href: "#how" },
  { label: "Family", href: "#family" },
  { label: "Live map", href: "#map" },
  { label: "Activity", href: "#activity" },
];

export function Navbar() {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-3.5"
    >
      <nav className="glass-strong flex w-full max-w-6xl items-center justify-between gap-4 rounded-full border border-line/80 px-4 py-2.5 shadow-soft">
        <a href="#top" aria-label="ScamShield AI home">
          <Logo />
        </a>
        <div className="hidden items-center gap-1 md:flex">
          {LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="rounded-full px-3.5 py-2 text-sm font-medium text-ink-soft transition-colors hover:bg-card hover:text-ink"
            >
              {l.label}
            </a>
          ))}
        </div>
        <Button size="sm" onClick={focusAnalyzer}>
          Analyze a message <ArrowRight className="h-4 w-4" />
        </Button>
      </nav>
    </motion.header>
  );
}
