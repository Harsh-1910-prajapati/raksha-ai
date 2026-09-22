"use client";

import { Badge, Button, Card, EmptyState, ErrorBox, Spinner } from "@/components/ui";
import type { AIAnalysis } from "@/lib/types";

export default function AIAnalysisPanel({
  analysis,
  loading,
  error,
  onGenerate,
}: {
  analysis: AIAnalysis | null;
  loading: boolean;
  error: string | null;
  onGenerate: () => void;
}) {
  return (
    <Card
      title="Gemini AI Analysis"
      subtitle="Situation summary & decision support generated from risk-engine output"
      action={
        <Button onClick={onGenerate} disabled={loading} variant={analysis ? "secondary" : "primary"}>
          {loading ? "Analyzing…" : analysis ? "Regenerate" : "Generate AI Analysis"}
        </Button>
      }
    >
      {error && <ErrorBox message={error} onRetry={onGenerate} />}
      {loading && <div className="py-4"><Spinner label="Asking Gemini to reason over the risk-engine output…" /></div>}
      {!loading && !error && !analysis && (
        <EmptyState title="No AI analysis yet" hint="Run the simulation, then generate the AI analysis." />
      )}
      {!loading && !error && analysis && (
        <div className="space-y-5">
          <Section title="Situation Summary">
            <p className="text-sm leading-relaxed text-slate-700">{analysis.summary}</p>
          </Section>
          <ListSection title="Highest Priority Areas" items={analysis.priorityAreas} />
          <ListSection title="Infrastructure Concerns" items={analysis.infrastructureRisks} />
          <ListSection title="Recommended Actions" items={analysis.recommendedActions} />
          <ListSection title="Resource Priorities" items={analysis.resourcePriorities} />
          <ListSection title="Evacuation Considerations" items={analysis.evacuationConsiderations} />
          <ListSection title="Public Communication Guidance" items={analysis.communicationGuidance} />
          <ProviderNote provider={analysis.ai_provider} note={analysis.provider_note} />
        </div>
      )}
    </Card>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h4 className="mb-1.5 text-sm font-semibold text-slate-800">{title}</h4>
      {children}
    </div>
  );
}

function ListSection({ title, items }: { title: string; items: string[] }) {
  if (!items.length)
    return (
      <div className="text-sm text-slate-500">
        <span className="font-semibold text-slate-800">{title}:</span> not provided
      </div>
    );
  return (
    <Section title={title}>
      <ul className="space-y-1.5">
        {items.map((it, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-400" />
            {it}
          </li>
        ))}
      </ul>
    </Section>
  );
}

export function ProviderNote({ provider, note }: { provider: string; note: string }) {
  return (
    <div className="flex items-start gap-2 border-t border-slate-100 pt-3 text-xs text-slate-500">
      {provider === "gemini" ? (
        <Badge tone="green">Gemini live</Badge>
      ) : (
        <Badge tone="amber">DEMO · mock AI</Badge>
      )}
      <span className="opacity-90">
        {note ||
          (provider === "gemini"
            ? "Analysis generated with Google Gemini from deterministic risk-engine values."
            : "GEMINI_API_KEY not configured — deterministic mock analysis. Add a key to use live Gemini.")}
      </span>
    </div>
  );
}