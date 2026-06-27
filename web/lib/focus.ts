/** Scrolls to the hero analyzer and focuses its input. Used by every "Analyze" CTA. */
export function focusAnalyzer() {
  if (typeof document === "undefined") return;
  document.getElementById("top")?.scrollIntoView({ behavior: "smooth" });
  // Wait for the smooth scroll to settle before focusing.
  window.setTimeout(() => {
    const el = document.getElementById("analyzer-input") as HTMLElement | null;
    el?.focus();
  }, 480);
}
