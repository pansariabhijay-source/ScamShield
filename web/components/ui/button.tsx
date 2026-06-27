"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-2xl text-sm font-medium transition-all duration-200 ease-[cubic-bezier(0.22,1,0.36,1)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-trust-400 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98] select-none",
  {
    variants: {
      variant: {
        primary:
          "bg-trust-500 text-white shadow-[0_8px_30px_-6px_rgba(168,85,247,0.6)] hover:bg-trust-600 hover:shadow-[0_12px_38px_-6px_rgba(168,85,247,0.7)]",
        secondary:
          "bg-white/[0.06] text-ink border border-white/[0.10] backdrop-blur-md hover:bg-white/[0.10] hover:border-trust-300/50",
        ghost: "text-ink-soft hover:bg-white/[0.06] hover:text-ink",
        subtle: "bg-white/[0.06] text-ink hover:bg-trust-50 hover:text-trust-700",
      },
      size: {
        sm: "h-9 px-4",
        md: "h-11 px-5",
        lg: "h-13 px-7 text-[15px]",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  ),
);
Button.displayName = "Button";

export { buttonVariants };
