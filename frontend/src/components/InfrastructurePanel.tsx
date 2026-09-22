"use client";

import { useMemo, useState } from "react";
import { Badge, Card, EmptyState, LevelBadge } from "@/components/ui";
import { INFRA_LABEL } from "@/lib/risk";
import type { InfrastructureSet } from "@/lib/types";

const PRIORITY_TONE: Record<number, "red" | "amber" | "slate"> = {
  1: "red",
  2: "amber",
  3: "slate",
};

export default function InfrastructurePanel({ set }: { set: InfrastructureSet }) {
  const [filter, setFilter] = useState<string | null>(null);

  const items = useMemo(() => {
    const filtered = filter ? set.items.filter((i) => i.type === filter) : set.items;
    return [...filtered].sort((a, b) => a.priority - b.priority || b.riskScore - a.riskScore);
  }, [set.items, filter]);

  if (!set.items.length) {
    return (
      <Card title="Critical Infrastructure" subtitle={set.note}>
        <EmptyState title="No infrastructure assets returned" hint="Try a larger impact radius or another district." />
      </Card>
    );
  }

  return (
    <Card
      title="Critical Infrastructure"
      subtitle={set.note}
      action={
        <span className="text-xs text-slate-400">
          {items.length} shown of {set.items.length}
        </span>
      }
    >
      <div className="mb-3 flex flex-wrap gap-1.5">
        {Object.entries(set.counts).map(([type, count]) => (
          <button
            key={type}
            onClick={() => setFilter(filter === type ? null : type)}
            className={`rounded border px-2 py-1 text-xs font-medium transition-colors ${
              filter === type
                ? "border-slate-900 bg-slate-900 text-white"
                : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
            }`}
          >
            {INFRA_LABEL[type] ?? type} · {count}
          </button>
        ))}
      </div>

      <div className="space-y-2.5">
        {items.map((it) => (
          <div
            key={it.id}
            className="rounded-lg border border-slate-200 bg-slate-50/60 p-3"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-slate-800">{it.name}</p>
                <p className="text-xs text-slate-500">
                  {INFRA_LABEL[it.type] ?? it.type}
                  {it.capacity ? ` · capacity ${it.capacity.toLocaleString()}` : ""}
                  {it.geometry === "line" ? " · road corridor" : ""}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge tone={PRIORITY_TONE[it.priority]}>Priority {it.priority}</Badge>
                <LevelBadge level={it.riskLevel} score={Math.round(it.riskScore)} />
              </div>
            </div>
            {it.threats.length > 0 && (
              <p className="mt-2 text-xs text-slate-600">
                <span className="font-medium">Threat: </span>
                {it.threats.join(" + ")}
              </p>
            )}
            {it.recommendation && (
              <p className="mt-1 text-xs text-slate-600">
                <span className="font-medium">Recommended action: </span>
                {it.recommendation}
              </p>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}