"use client";

import { Badge, Button, Card, EmptyState, ErrorBox, Spinner } from "@/components/ui";
import { ProviderNote } from "@/components/AIAnalysisPanel";
import type { ActionPlan } from "@/lib/types";

const PHASES = [
  { key: "immediateActions", title: "Immediate", tone: "red" as const },
  { key: "beforeImpact", title: "Before Impact", tone: "amber" as const },
  { key: "duringEvent", title: "During Event", tone: "blue" as const },
  { key: "recovery", title: "Recovery Preparation", tone: "green" as const },
];

export default function ActionPlanPanel({
  plan,
  loading,
  error,
  onGenerate,
}: {
  plan: ActionPlan | null;
  loading: boolean;
  error: string | null;
  onGenerate: () => void;
}) {
  return (
    <Card
      title="Emergency Action Plan"
      subtitle="Phased response actions for the scenario"
      action={
        <Button onClick={onGenerate} disabled={loading} variant={plan ? "secondary" : "primary"}>
          {loading ? "Planning…" : plan ? "Regenerate" : "Generate Action Plan"}
        </Button>
      }
    >
      {error && <ErrorBox message={error} onRetry={onGenerate} />}
      {loading && <div className="py-4"><Spinner label="Drafting phased emergency actions…" /></div>}
      {!loading && !error && !plan && (
        <EmptyState title="No action plan yet" hint="Generate the AI action plan after running a simulation." />
      )}
      {!loading && !error && plan && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {PHASES.map((phase) => (
              <div key={phase.key} className="rounded-lg border border-slate-200 p-4">
                <Badge tone={phase.tone}>{phase.title}</Badge>
                <ul className="mt-2.5 space-y-1.5">
                  {(plan[phase.key as keyof ActionPlan] as string[]).map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-400" />
                      {item}
                    </li>
                  ))}
                  {!(plan[phase.key as keyof ActionPlan] as string[]).length && (
                    <li className="text-sm text-slate-500">No items listed.</li>
                  )}
                </ul>
              </div>
            ))}
          </div>
          <ProviderNote provider={plan.ai_provider} note={plan.provider_note} />
        </div>
      )}
    </Card>
  );
}