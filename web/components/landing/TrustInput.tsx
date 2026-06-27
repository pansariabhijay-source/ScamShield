"use client";

import { useRef, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import {
  MessageSquareText,
  ImageUp,
  Link2,
  QrCode,
  IndianRupee,
  Sparkles,
  ArrowRight,
  Loader2,
  UploadCloud,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { AnimatedPlaceholder } from "./AnimatedPlaceholder";
import { useAnalysis } from "@/store/useAnalysis";
import type { InputType } from "@/lib/types";
import { cn } from "@/lib/utils";

const MODES: { id: InputType; label: string; icon: typeof Link2 }[] = [
  { id: "TEXT", label: "Paste message", icon: MessageSquareText },
  { id: "IMAGE", label: "Upload screenshot", icon: ImageUp },
  { id: "URL", label: "Analyze URL", icon: Link2 },
  { id: "QR", label: "Scan QR", icon: QrCode },
  { id: "UPI", label: "Analyze UPI", icon: IndianRupee },
];

const EXAMPLE =
  "URGENT: Dear customer, your SBI account KYC is incomplete and will be blocked today. Verify immediately at http://sbi-kyc-verify.in to avoid suspension.";

// Canned content fed to the demo engine when a file/QR is "scanned".
const CANNED: Partial<Record<InputType, string>> = {
  IMAGE: EXAMPLE,
  QR: "UPI collect request: approve to receive ₹4,999 cashback from rewards@okaxis",
};

const PLACEHOLDER: Partial<Record<InputType, string>> = {
  URL: "https://sbi-kyc-verify.in/login",
  UPI: "name@bank, or paste a payment request",
};

export function TrustInput() {
  const { input, inputType, phase, setInput, setInputType, analyze } = useAnalysis();
  const fileRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const analyzing = phase === "analyzing";

  const isFileMode = inputType === "IMAGE" || inputType === "QR";
  const isLineMode = inputType === "URL" || inputType === "UPI";

  function switchMode(id: InputType) {
    setInputType(id);
    setFileName(null);
    setPreview(null);
  }

  function handleFile(file: File | undefined) {
    if (!file) return;
    setFileName(file.name);
    if (file.type.startsWith("image/")) setPreview(URL.createObjectURL(file));
    // Run the analysis with mode-appropriate demo content.
    analyze(CANNED[inputType] ?? "Uploaded file for analysis");
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 28, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.8, delay: 0.25, ease: [0.22, 1, 0.36, 1] }}
      className="group relative mx-auto w-full max-w-2xl"
    >
      <div className="pointer-events-none absolute -inset-3 -z-10 rounded-[32px] bg-[radial-gradient(60%_60%_at_50%_30%,rgba(59,108,246,0.18),transparent_70%)] opacity-0 blur-2xl transition-opacity duration-500 group-hover:opacity-100 group-focus-within:opacity-100" />

      <div className="glass-strong overflow-hidden rounded-[26px] border border-line shadow-float">
        {/* Mode tabs */}
        <div className="flex items-center gap-1 overflow-x-auto border-b border-line/70 px-2.5 py-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {MODES.map((m) => {
            const active = m.id === inputType;
            return (
              <button
                key={m.id}
                onClick={() => switchMode(m.id)}
                className={cn(
                  "relative flex shrink-0 items-center gap-1.5 rounded-full px-3.5 py-2 text-[13px] font-medium transition-colors",
                  active ? "text-trust-700" : "text-ink-faint hover:text-ink-soft",
                )}
              >
                {active && (
                  <motion.span
                    layoutId="modepill"
                    className="absolute inset-0 -z-10 rounded-full bg-trust-50"
                    transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  />
                )}
                <m.icon className="h-4 w-4" strokeWidth={2} />
                {m.label}
              </button>
            );
          })}
        </div>

        {/* Input body — varies by mode */}
        <div className="px-5 pb-4 pt-4">
          {inputType === "TEXT" && (
            <div className="relative min-h-[92px]">
              <AnimatedPlaceholder active={input.length === 0 && !analyzing} />
              <textarea
                id="analyzer-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") analyze();
                }}
                rows={3}
                aria-label="Paste a suspicious message to analyze"
                className="relative z-10 w-full resize-none bg-transparent text-[17px] leading-relaxed text-ink outline-none placeholder:text-transparent"
              />
            </div>
          )}

          {isLineMode && (
            <div className="flex min-h-[92px] items-center">
              <input
                id="analyzer-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") analyze();
                }}
                placeholder={PLACEHOLDER[inputType]}
                aria-label={inputType === "URL" ? "Enter a URL to analyze" : "Enter a UPI ID or request"}
                className="w-full bg-transparent text-[17px] text-ink outline-none placeholder:text-ink-faint"
              />
            </div>
          )}

          {isFileMode && (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragging(false);
                handleFile(e.dataTransfer.files?.[0]);
              }}
              onClick={() => !preview && fileRef.current?.click()}
              className={cn(
                "flex min-h-[120px] cursor-pointer items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-4 text-center transition-colors",
                dragging ? "border-trust-400 bg-trust-50" : "border-line hover:border-trust-200 hover:bg-offwhite",
              )}
            >
              <input
                id="analyzer-input"
                ref={fileRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => handleFile(e.target.files?.[0] ?? undefined)}
              />
              {preview ? (
                <div className="flex items-center gap-3">
                  <Image src={preview} alt="Uploaded preview" width={56} height={56} unoptimized className="h-14 w-14 rounded-xl object-cover shadow-soft" />
                  <div className="text-left">
                    <p className="max-w-[200px] truncate text-[14px] font-medium text-ink">{fileName}</p>
                    <p className="text-[13px] text-trust-600">Analyzing…</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setPreview(null);
                      setFileName(null);
                    }}
                    className="grid h-7 w-7 place-items-center rounded-full text-ink-faint hover:bg-card"
                    aria-label="Remove file"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2 py-2 text-ink-faint">
                  <span className="grid h-11 w-11 place-items-center rounded-2xl bg-trust-50 text-trust-500">
                    <UploadCloud className="h-5 w-5" />
                  </span>
                  <p className="text-[14.5px] font-medium text-ink-soft">
                    {inputType === "QR" ? "Drop a QR screenshot to scan" : "Drop a screenshot or click to upload"}
                  </p>
                  <p className="text-[12.5px]">PNG, JPG · up to 10MB · never stored</p>
                </div>
              )}
            </div>
          )}

          <div className="mt-3 flex items-center justify-between gap-3">
            <div className="flex items-center gap-1.5 text-[12.5px] text-ink-faint">
              <Sparkles className="h-3.5 w-3.5 text-trust-400" />
              <span className="hidden sm:inline">Private & on-device first</span>
              <span className="sm:hidden">Private</span>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="md"
                onClick={() => {
                  switchMode("TEXT");
                  analyze(EXAMPLE);
                }}
                disabled={analyzing}
                className="hidden sm:inline-flex"
              >
                See example analysis
              </Button>
              {!isFileMode && (
                <Button size="md" onClick={() => analyze()} disabled={analyzing || input.trim().length === 0}>
                  {analyzing ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" /> Analyzing…
                    </>
                  ) : (
                    <>
                      Analyze trust <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      <p className="mt-3 text-center text-[13px] text-ink-faint">
        {isFileMode ? (
          <>Drop a file above. Results appear instantly · We never store your uploads</>
        ) : (
          <>
            Press{" "}
            <kbd className="rounded-md border border-white/10 bg-white/[0.08] px-1.5 py-0.5 text-[11px] font-medium text-ink-soft shadow-soft">
              {inputType === "TEXT" ? "⌘ ↵" : "↵"}
            </kbd>{" "}
            to analyze · We never store your messages
          </>
        )}
      </p>
    </motion.div>
  );
}
