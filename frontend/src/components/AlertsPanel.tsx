"use client";

import { useState } from "react";
import { Badge, Button, Card, ErrorBox, Spinner } from "@/components/ui";
import { ProviderNote } from "@/components/AIAnalysisPanel";
import type { AlertContent } from "@/lib/types";

const LANG_NAMES: Record<string, string> = { en: "English", hi: "Hindi", te: "Telugu" };

export default function AlertsPanel({
  citizen,
  authority,
  loading,
  loadingAuthority,
  error,
  onGenerateCitizen,
  onGenerateAuthority,
}: {
  citizen: AlertContent | null;
  authority: AlertContent | null;
  loading: boolean;
  loadingAuthority: boolean;
  error: string | null;
  onGenerateCitizen: () => void;
  onGenerateAuthority: () => void;
}) {
  const [lang, setLang] = useState<"en" | "hi" | "te">("en");
  const active = citizen && (citizen.languages.find((l) => l.language === lang) || citizen.languages[0]);

  return (
    <Card
      title="Multilingual Alerts"
      subtitle="Citizen & authority preparedness messages (English, Hindi, Telugu)"
      action={
        <div className="flex gap-1 rounded-md border border-slate-200 bg-slate-100 p-0.5">
          {(["en", "hi", "te"] as const).map((code) => (
            <button
              key={code}
              onClick={() => setLang(code)}
              className={`rounded px-2 py-0.5 text-xs font-medium transition-colors ${
                lang === code ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-800"
              }`}
            >
              {LANG_NAMES[code]}
            </button>
          ))}
        </div>
      }
    >
      {error && <ErrorBox message={error} onRetry={onGenerateCitizen} />}

      <div className="mb-4 rounded-lg border border-slate-200 bg-slate-50/70 p-4">
        <div className="mb-2 flex items-center justify-between">
          <Badge tone="blue">Citizen Alert</Badge>
          <Button onClick={onGenerateCitizen} disabled={loading} variant="secondary" className="px-3 py-1.5 text-xs">
            {loading ? "Drafting…" : citizen ? "Regenerate" : "Generate Citizen Alert"}
          </Button>
        </div>
        {loading ? (
          <Spinner label="Drafting multilingual citizen alert…" />
        ) : !citizen ? (
          <p className="text-sm text-slate-500">No citizen alert generated.</p>
        ) : (
          <div className="space-y-2">
            <p className="text-sm font-bold text-slate-900">{active?.title ?? citizen.title}</p>
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700">{active?.body ?? citizen.summary}</p>
            <p className="text-[11px] text-slate-400">{citizen.disclaimer}</p>
          </div>
        )}
      </div>

      <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-4">
        <div className="mb-2 flex items-center justify-between">
          <Badge tone="purple">Authority Alert</Badge>
          <Button onClick={onGenerateAuthority} disabled={loadingAuthority} variant="secondary" className="px-3 py-1.5 text-xs">
            {loadingAuthority ? "Drafting…" : authority ? "Regenerate" : "Generate Authority Alert"}
          </Button>
        </div>
        {loadingAuthority ? (
          <Spinner label="Drafting authority briefing…" />
        ) : !authority ? (
          <p className="text-sm text-slate-500">No authority alert generated.</p>
        ) : (
          <div className="space-y-2">
            <p className="text-sm font-bold text-slate-900">
              {authority.languages.find((l) => l.language === lang)?.title ?? authority.title}
            </p>
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
              {authority.languages.find((l) => l.language === lang)?.body ?? authority.summary}
            </p>
          </div>
        )}
      </div>

      {(citizen || authority) && (
        <div className="mt-4">
          <ProviderNote provider={citizen?.ai_provider ?? authority?.ai_provider ?? "mock"} note={citizen?.provider_note ?? authority?.provider_note ?? ""} />
        </div>
      )}
    </Card>
  );
}