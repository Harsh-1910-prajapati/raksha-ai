"use client";

import { Card, LevelBadge } from "@/components/ui";
import { RISK_STYLES } from "@/lib/risk";
import type { RiskResult } from "@/lib/types";

export default function RiskBreakdown({ risk }: { risk: RiskResult }) {
  const components = Object.values(risk.components);

  return (
    <Card
      title="Risk Breakdown"
      subtitle={risk.overall.label}
      action={<LevelBadge level={risk.overall.level} score={Math.round(risk.overall.score)} />}
    >
      <div className="space-y-4">
        {components.map((c) => {
          const style = RISK_STYLES[c.level];
          return (
            <div key={c.name}>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="font-medium text-slate-700">{c.name}</span>
                <span className="text-xs text-slate-500">
                  {Math.round(c.score)}/100 · weight {(c.weight * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${Math.min(100, c.score)}%`,
                    backgroundColor:
                      c.score >= 76
                        ? "#dc2626"
                        : c.score >= 51
                          ? "#f97316"
                          : c.score >= 26
                            ? "#f59e0b"
                            : "#10b981",
                  }}
                />
              </div>
              <div className="mt-1.5 text-xs text-slate-500">
                <span className={`mr-1 inline-block rounded px-1.5 py-px font-medium ${style.bg} ${style.text}`}>
                  {c.level}
                </span>
                {c.factors.length ? c.factors.join(" · ") : "No dominant factors"}
              </div>
            </div>
          );
        })}
      </div>
      <p className="mt-4 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-[11px] text-amber-800">
        {risk.overall.weightsNote}
      </p>
    </Card>
  );
}