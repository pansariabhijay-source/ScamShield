"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { SectionHeading } from "./SectionHeading";
import { Card } from "@/components/ui/card";
import { DEMO_STATS, NODE_POSITIONS } from "@/lib/mock";
import { fetchStats, toneForCategory } from "@/lib/stats";
import { VERDICT } from "@/lib/verdict";
import { cn } from "@/lib/utils";

export function ScamMap() {
  const { data, isError, isLoading } = useQuery({
    queryKey: ["stats", "overview"],
    queryFn: fetchStats,
    retry: false,
    staleTime: 60_000,
  });

  // Live only when the backend answered with real volume. Otherwise fall back
  // to demo numbers and say so plainly.
  const live = !!data && data.total_this_week > 0;
  const stats = live ? data : DEMO_STATS;

  const maxCount = Math.max(...stats.categories.map((c) => c.count), 1);
  const nodes = stats.categories.slice(0, NODE_POSITIONS.length).map((c, i) => ({
    ...c,
    ...NODE_POSITIONS[i],
    tone: toneForCategory(c.category),
  }));

  return (
    <section id="map" className="px-5 py-24">
      <div className="mx-auto max-w-6xl">
        <SectionHeading
          eyebrow="Live intelligence"
          title="Scam activity, in real time"
          subtitle="ScamShield learns from every report. See which scams are spiking this week, and stay a step ahead."
        />

        <div className="mt-14 grid gap-5 lg:grid-cols-[1.5fr_1fr]">
          {/* Activity field */}
          <Card className="relative overflow-hidden p-0">
            <div className="grid-dots aura relative h-[460px] w-full">
              <div className="absolute left-5 top-5 z-20 flex items-center gap-4 rounded-full border border-white/10 bg-card/70 px-4 py-2 text-[12.5px] font-medium text-ink-soft shadow-soft backdrop-blur">
                <span className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-scam-500" /> Critical
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-warn-500" /> Elevated
                </span>
              </div>

              {nodes.map((n, i) => {
                const v = VERDICT[n.tone];
                const size = 12 + (n.count / maxCount) * 26;
                return (
                  <motion.div
                    key={n.category}
                    initial={{ opacity: 0, scale: 0 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 + i * 0.08, type: "spring", stiffness: 220, damping: 18 }}
                    className="group absolute -translate-x-1/2 -translate-y-1/2"
                    style={{ left: `${n.x}%`, top: `${n.y}%` }}
                  >
                    <span
                      className="block rounded-full blur-md"
                      style={{ width: size * 3, height: size * 3, background: v.soft, position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%)" }}
                    />
                    <span className="relative block rounded-full" style={{ color: v.ring }}>
                      <span className="live-pulse absolute inset-0 rounded-full opacity-50" />
                      <span className="relative block rounded-full ring-4 ring-canvas" style={{ width: size, height: size, background: v.ring }} />
                    </span>
                    <div className="pointer-events-none absolute left-1/2 top-full z-30 mt-2 w-max -translate-x-1/2 rounded-xl border border-white/10 bg-card px-3 py-2 text-left opacity-0 shadow-card transition-opacity duration-200 group-hover:opacity-100">
                      <p className="text-[13px] font-semibold text-ink">{n.category}</p>
                      <p className="text-[12px] text-ink-faint">
                        {n.count.toLocaleString("en-IN")} reports this week
                      </p>
                    </div>
                  </motion.div>
                );
              })}

              <span className="absolute bottom-5 right-6 flex items-center gap-1.5 text-[12px] font-medium text-ink-faint">
                <span
                  className={cn("h-1.5 w-1.5 rounded-full", live ? "bg-safe-500" : "bg-ink-faint")}
                />
                {isLoading
                  ? "Connecting…"
                  : live
                    ? "Live · synced just now"
                    : isError
                      ? "Sample data · API offline"
                      : "Sample data · no reports yet"}
              </span>
            </div>
          </Card>

          {/* Side panel */}
          <div className="flex flex-col gap-5">
            <Card className="px-6 py-6">
              <p className="text-[13px] font-semibold text-ink-faint">Reports this week</p>
              <div className="mt-1 flex items-end gap-2">
                <span className="text-3xl font-semibold tracking-tight text-ink">
                  {stats.total_this_week.toLocaleString("en-IN")}
                </span>
                <span
                  className={cn(
                    "mb-1 text-[13px] font-medium",
                    stats.pct_change >= 0 ? "text-scam-600" : "text-safe-600",
                  )}
                >
                  {stats.pct_change >= 0 ? "↑" : "↓"} {Math.abs(stats.pct_change)}%
                </span>
              </div>
              <div className="mt-3 h-24">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={stats.trend} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
                    <defs>
                      <linearGradient id="trend" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#a855f7" stopOpacity={0.45} />
                        <stop offset="100%" stopColor="#a855f7" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="label" hide />
                    <YAxis hide domain={["dataMin - 200", "dataMax + 100"]} />
                    <Tooltip
                      cursor={{ stroke: "#6d4fb0", strokeWidth: 1 }}
                      contentStyle={{
                        borderRadius: 12,
                        border: "1px solid #2a2440",
                        background: "#140f24",
                        color: "#f4f1fb",
                        boxShadow: "0 12px 32px -12px rgba(0,0,0,.6)",
                        fontSize: 12,
                      }}
                      labelStyle={{ color: "#b8b1cf" }}
                    />
                    <Area type="monotone" dataKey="count" stroke="#a855f7" strokeWidth={2.5} fill="url(#trend)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card className="px-6 py-5">
              <p className="text-[13px] font-semibold text-ink-faint">Top scam types this week</p>
              <div className="mt-3 space-y-1">
                {stats.categories.slice(0, 5).map((c) => {
                  const v = VERDICT[toneForCategory(c.category)];
                  return (
                    <div key={c.category} className="flex items-center justify-between rounded-xl px-2 py-2 transition-colors hover:bg-offwhite">
                      <span className="flex items-center gap-2.5">
                        <span className="h-2 w-2 rounded-full" style={{ background: v.ring }} />
                        <span className="text-[14px] font-medium text-ink">{c.category}</span>
                      </span>
                      <span className="text-[13px] font-semibold text-ink-soft">
                        {c.count.toLocaleString("en-IN")}
                      </span>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}
