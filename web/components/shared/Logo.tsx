import Image from "next/image";
import { cn } from "@/lib/utils";

/** Brand mark — the ScamShield app icon + wordmark. */
export function Logo({ className, size = 34 }: { className?: string; size?: number }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <Image
        src="/brand-mark.png"
        alt="ScamShield AI"
        width={size}
        height={size}
        priority
        className="rounded-[10px] shadow-[0_4px_12px_-4px_rgba(16,24,40,0.25)]"
      />
      <span className="text-[17px] font-semibold tracking-tight text-ink">
        ScamShield<span className="text-trust-500"> AI</span>
      </span>
    </div>
  );
}
