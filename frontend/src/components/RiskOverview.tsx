"use client";

import { formatPopulation } from "@/lib/risk";
import type { Simulation } from "@/lib/types";

export default function RiskOverview({ simulation }: { simulation: Simulation }) {
  const { risk, exposure, highRiskAreas, infrastructure } = simulation;

  const highOrCritical = infrastructure.items.filter(
    (i) => i.riskLevel === "HIGH" || i.riskLevel === "CRITICAL"
  ).length;

  const kpis = [
    {
      label: "Overall Risk",
      value: `${Math.round(risk.overall.score)}`,
      unit: "/ 100",
      sub: risk.overall.level,
      accent: risk.overall.score >= 76 ? "text-red-700" : risk.overall.score >= 51 ? "text-orange-700" : risk.overall.score >= 26 ? "text-amber-700" : "text-emerald-700",
    },
    {
      label: "High-Risk Zones",
      value: `${highRiskAreas.length}`,
      unit: "",
      sub: risk.overall.level === "CRITICAL" ? "elevated area" : "flagged sectors",
      accent: "text-slate-900",
    },
    {
      label: "Critical Infrastructure",
      value: `${highOrCritical}`,
      unit: "assets",
      sub: "HIGH / CRITICAL",
      accent: "text-slate-900",
    },
    {
      label: "Population Exposed",
      value: formatPopulation(exposure.populationExposed),
      unit: "",
      sub: `${exposure.areaSqKm.toLocaleString()} km² modelled`,
      accent: "text-slate-900",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {kpis.map((k) => (
        <div key={k.label} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{k.label}</p>
          <p className={`mt-1 flex items-end gap-1 text-3xl font-bold ${k.accent}`}>
            {k.value}
            {k.unit && <span className="pb-1 text-xs font-medium text-slate-400">{k.unit}</span>}
          </p>
          <p className="mt-1 text-xs text-slate-500">{k.sub}</p>
        </div>
      ))}
    </div>
  );
}