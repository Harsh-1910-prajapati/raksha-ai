"use client";

import { Badge, Button, Card, EmptyState, ErrorBox, Spinner } from "@/components/ui";
import { ProviderNote } from "@/components/AIAnalysisPanel";
import type { StateBrief } from "@/lib/types";

export default function StateBriefPanel({
  brief,
  loading,
  error,
  onGenerate,
}: {
  brief: StateBrief | null;
  loading: boolean;
  error: string | null;
  onGenerate: () => void;
}) {
  return (
    <Card
      title="State Emergency Brief"
      subtitle="Printable state-level summary for coordination"
      action={
        <div className="flex gap-2">
          {brief && (
            <Button onClick={() => window.print()} variant="secondary" className="px-3 py-1.5 text-xs">
              Print / PDF
            </Button>
          )}
          <Button onClick={onGenerate} disabled={loading} variant={brief ? "secondary" : "primary"} className="px-3 py-1.5 text-xs">
            {loading ? "Preparing…" : brief ? "Regenerate" : "Generate State Emergency Brief"}
          </Button>
        </div>
      }
    >
      {error && <ErrorBox message={error} onRetry={onGenerate} />}
      {loading && <div className="py-4"><Spinner label="Assembling state-level brief…" /></div>}
      {!loading && !error && !brief && (
        <EmptyState title="No state brief yet" hint="Generate the state emergency brief from the current simulation." />
      )}
      {!loading && !error && brief && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="red">State-level</Badge>
            <span className="text-sm font-semibold text-slate-800">{brief.state}</span>
            <span className="text-xs text-slate-400">generated {new Date(brief.generatedAt).toLocaleString()}</span>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {Object.entries(brief.criticalInfrastructure).map(([k, v]) => (
              <div key={k} className="rounded-md border border-slate-200 bg-white px-3 py-2 text-center">
                <p className="text-2xl font-bold text-slate-900">{v}</p>
                <p className="text-xs capitalize text-slate-500">{k}</p>
              </div>
            ))}
          </div>

          <Row label="Affected districts" items={brief.affectedDistricts} />
          <Row label="High-risk zones" items={brief.highRiskZones} />
          <Row label="Hospitals at risk" items={brief.hospitalsAtRisk} />
          <Row label="Shelters at risk" items={brief.sheltersAtRisk} />
          <Row label="Accessibility issues" items={brief.accessibilityIssues} />
          <Row label="Recommended priorities" items={brief.recommendedPriorities} />

          <div>
            <h4 className="mb-1.5 text-sm font-semibold text-slate-800">Communication message</h4>
            <p className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
              {brief.communicationMessage}
            </p>
          </div>

          <p className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-[11px] text-amber-800">
            {brief.disclaimer}
          </p>
          <ProviderNote provider={brief.ai_provider} note={brief.provider_note} />
        </div>
      )}
    </Card>
  );
}

function Row({ label, items }: { label: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div>
      <h4 className="mb-1.5 text-sm font-semibold text-slate-800">{label}</h4>
      <ul className="space-y-1">
        {items.map((it, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-400" />
            {it}
          </li>
        ))}
      </ul>
    </div>
  );
}