import { create } from "zustand";
import type { DetectionResult, InputType } from "@/lib/types";
import { analyzeText } from "@/lib/api";

type Phase = "idle" | "analyzing" | "done" | "error";

interface AnalysisState {
  phase: Phase;
  input: string;
  inputType: InputType;
  result: DetectionResult | null;
  error: string | null;
  setInput: (v: string) => void;
  setInputType: (t: InputType) => void;
  analyze: (override?: string) => Promise<void>;
  reset: () => void;
}

export const useAnalysis = create<AnalysisState>((set, get) => ({
  phase: "idle",
  input: "",
  inputType: "TEXT",
  result: null,
  error: null,
  setInput: (v) => set({ input: v }),
  setInputType: (t) => set({ inputType: t }),
  analyze: async (override) => {
    const content = (override ?? get().input).trim();
    if (!content) return;
    set({ phase: "analyzing", error: null, result: null, input: content });
    try {
      const result = await analyzeText(content, get().inputType);
      set({ result, phase: "done" });
    } catch (e) {
      set({ phase: "error", error: e instanceof Error ? e.message : "Something went wrong" });
    }
  },
  reset: () => set({ phase: "idle", result: null, error: null, input: "" }),
}));
