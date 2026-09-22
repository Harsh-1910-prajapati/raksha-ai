"use client";

import { useEffect, useState } from "react";
import { api, API_URL } from "@/lib/api";

export default function Header() {
  const [backendUp, setBackendUp] = useState<boolean | null>(null);
  const [geminiLive, setGeminiLive] = useState<boolean | null>(null);
  const [earthEngine, setEarthEngine] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    api
      .health()
      .then((h) => {
        if (!mounted) return;
        const providers = h.providers as Record<string, { provider?: string }>;
        setBackendUp(true);
        setGeminiLive(providers.ai?.provider === "gemini");
        const geo = h.earthEngine as { provider?: string };
        setEarthEngine(geo?.provider === "earth-engine");
      })
      .catch(() => mounted && setBackendUp(false));
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-[1400px] flex-wrap items-center justify-between gap-3 px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-slate-900 text-lg font-bold text-white">
            र
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              RakshaAI
            </h1>
            <p className="text-xs text-slate-500">
              AI-Powered Pre-Disaster Intelligence
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <StatusDot ok={backendUp} label="Backend" />
          <StatusDot
            ok={geminiLive}
            warn={backendUp === true && geminiLive === false}
            label="Gemini"
            warnLabel="Gemini: mock fallback"
          />
          <StatusDot
            ok={earthEngine}
            warn={backendUp === true && earthEngine === false}
            label="Earth Engine"
            warnLabel="Earth Engine: demo provider"
          />
          <span className="ml-1 hidden rounded border border-slate-200 bg-slate-50 px-2 py-1 font-mono text-[10px] text-slate-500 sm:inline-block">
            {API_URL}
          </span>
        </div>
      </div>
    </header>
  );
}

function StatusDot({
  ok,
  warn,
  label,
  warnLabel,
}: {
  ok: boolean | null;
  warn?: boolean;
  label: string;
  warnLabel?: string;
}) {
  if (ok === null)
    return (
      <span className="inline-flex items-center gap-1.5 rounded border border-slate-200 px-2 py-1 text-slate-500">
        <span className="h-2 w-2 rounded-full bg-slate-300" />
        {label}: checking…
      </span>
    );
  if (warn)
    return (
      <span
        className="inline-flex items-center gap-1.5 rounded border border-amber-200 bg-amber-50 px-2 py-1 text-amber-800"
        title={warnLabel}
      >
        <span className="h-2 w-2 rounded-full bg-amber-400" />
        {label}: demo fallback
      </span>
    );
  if (!ok)
    return (
      <span
        className="inline-flex items-center gap-1.5 rounded border border-red-200 bg-red-50 px-2 py-1 text-red-700"
        title="Backend not reachable"
      >
        <span className="h-2 w-2 rounded-full bg-red-400" />
        {label}: offline
      </span>
    );
  return (
    <span className="inline-flex items-center gap-1.5 rounded border border-emerald-200 bg-emerald-50 px-2 py-1 text-emerald-700">
      <span className="h-2 w-2 rounded-full bg-emerald-500" />
      {label}: live
    </span>
  );
}