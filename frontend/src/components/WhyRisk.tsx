"use client";

import { Card, LevelBadge } from "@/components/ui";
import type { ZoneRisk } from "@/lib/types";

function colorFor(level: string): string {
  return (
    {
      LOW: "#10b981",
      MODERATE: "#f59e0b",
      HIGH: "#f97316",
      CRITICAL: "#dc2626",
    }[level] ?? "#94a3b8"
  );
}

export default function WhyRisk({
  zones,
  selectedZoneId,
}: {
  zones: ZoneRisk[];
  selectedZoneId: string | null;
}) {
  const sorted = [...zones].sort((a, b) => b.riskScore - a.riskScore);
  const top = sorted[0];
  const selected = sorted.find((z) => z.id === selectedZoneId) ?? top;

  if (!selected) {
    return <Card title="Why is this area at risk?"><p className="text-sm text-slate-500">No zone data yet.</p></Card>;
  }

  return (
    <Card title="Why is this area at risk?" subtitle={`Sector selectable on the map · deterministic risk factors`}>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-slate-800">{selected.label}</p>
          <p className="text-xs text-slate-500">
            {selected.distanceKm.toFixed(0)} km from centre · {selected.elevationM.toFixed(0)} m elevation
          </p>
        </div>
        <LevelBadge level={selected.riskLevel} score={Math.round(selected.riskScore)} />
      </div>
      <ul className="space-y-1.5">
        {selected.factors.map((f) => (
          <li key={f} className="flex items-start gap-2 text-sm text-slate-700">
            <svg className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" viewBox="0 0 20 20" fill="currentColor" aria-hidden>
              <path fillRule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clipRule="evenodd" />
            </svg>
            {f}
          </li>
        ))}
        {!selected.factors.length && <li className="text-sm text-slate-500">No dominant factors recorded.</li>}
      </ul>

      <div className="mt-4 border-t border-slate-100 pt-3">
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
          All sectors by risk
        </p>
        <div className="space-y-1">
          {sorted.slice(0, 6).map((z) => (
            <div key={z.id} className="flex items-center justify-between gap-2 text-xs">
              <span className="truncate text-slate-600">{z.label}</span>
              <span className="flex items-center gap-1.5">
                <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: colorFor(z.riskLevel) }} />
                <span className="tabular-nums text-slate-500">{Math.round(z.riskScore)}</span>
                <span className="w-16 text-right text-slate-400">{z.riskLevel}</span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}