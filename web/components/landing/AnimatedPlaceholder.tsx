"use client";

import { useEffect, useState } from "react";

const SAMPLES = [
  "Your KYC will expire today. Update now: bit.ly/sbi-kyc…",
  "Congratulations! You won ₹25,00,000 in the lucky draw…",
  "Amazon work from home, earn ₹3,000/day, register here…",
  "Rahul requested ₹5,000 via UPI. Approve to receive…",
];

/** Typewriter that types, holds, deletes, and cycles. Shown only when empty. */
export function AnimatedPlaceholder({ active }: { active: boolean }) {
  const [text, setText] = useState("");
  const [i, setI] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!active) return;
    const full = SAMPLES[i];
    let delay = deleting ? 28 : 46;
    if (!deleting && text === full) delay = 1500;
    if (deleting && text === "") delay = 320;

    const t = setTimeout(() => {
      if (!deleting && text === full) {
        setDeleting(true);
      } else if (deleting && text === "") {
        setDeleting(false);
        setI((p) => (p + 1) % SAMPLES.length);
      } else {
        setText(full.slice(0, deleting ? text.length - 1 : text.length + 1));
      }
    }, delay);
    return () => clearTimeout(t);
  }, [text, deleting, i, active]);

  if (!active) return null;

  return (
    <span className="pointer-events-none absolute left-0 top-0 text-[17px] leading-relaxed text-ink-faint">
      {text}
      <span className="caret ml-0.5 inline-block h-[1.05em] w-[2px] translate-y-[3px] bg-trust-400" />
    </span>
  );
}
