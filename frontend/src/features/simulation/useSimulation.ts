"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type {
  AIAnalysis,
  ActionPlan,
  AlertContent,
  ScenarioInput,
  Simulation,
  StateBrief,
} from "@/lib/types";

export interface PanelState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

const emptyPanel = <T,>(): PanelState<T> => ({ data: null, loading: false, error: null });

export function useRakshaSimulation() {
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const [selectedZoneId, setSelectedZoneId] = useState<string | null>(null);

  const [analysis, setAnalysis] = useState<PanelState<AIAnalysis>>(emptyPanel<AIAnalysis>());
  const [plan, setPlan] = useState<PanelState<ActionPlan>>(emptyPanel<ActionPlan>());
  const [citizenAlert, setCitizenAlert] = useState<PanelState<AlertContent>>(emptyPanel<AlertContent>());
  const [authorityAlert, setAuthorityAlert] = useState<PanelState<AlertContent>>(emptyPanel<AlertContent>());
  const [brief, setBrief] = useState<PanelState<StateBrief>>(emptyPanel<StateBrief>());

  const resetPanels = () => {
    setAnalysis(emptyPanel<AIAnalysis>());
    setPlan(emptyPanel<ActionPlan>());
    setCitizenAlert(emptyPanel<AlertContent>());
    setAuthorityAlert(emptyPanel<AlertContent>());
    setBrief(emptyPanel<StateBrief>());
  };

  const run = async (input: ScenarioInput) => {
    setRunning(true);
    setRunError(null);
    setSimulation(null);
    setSelectedZoneId(null);
    resetPanels();
    try {
      const sim = await api.simulate(input);
      setSimulation(sim);
      // Auto-generate the core AI deliverables after each run for a fast demo.
      void generateAnalysis(sim);
      void generatePlan(sim);
    } catch (err) {
      setRunError(err instanceof Error ? err.message : "Simulation failed");
    } finally {
      setRunning(false);
    }
  };

  const generateAnalysis = async (target?: Simulation) => {
    const sim = target ?? simulation;
    if (!sim) return;
    setAnalysis({ data: null, loading: true, error: null });
    try {
      setAnalysis({ data: await api.aiAnalyze(sim), loading: false, error: null });
    } catch (err) {
      setAnalysis({ data: null, loading: false, error: err instanceof Error ? err.message : "AI analysis failed" });
    }
  };

  const generatePlan = async (target?: Simulation) => {
    const sim = target ?? simulation;
    if (!sim) return;
    setPlan({ data: null, loading: true, error: null });
    try {
      setPlan({ data: await api.aiActionPlan(sim), loading: false, error: null });
    } catch (err) {
      setPlan({ data: null, loading: false, error: err instanceof Error ? err.message : "Action plan failed" });
    }
  };

  const generateCitizenAlert = async () => {
    if (!simulation) return;
    setCitizenAlert({ data: null, loading: true, error: null });
    try {
      setCitizenAlert({ data: await api.aiAlert(simulation, "citizen"), loading: false, error: null });
    } catch (err) {
      setCitizenAlert({ data: null, loading: false, error: err instanceof Error ? err.message : "Alert failed" });
    }
  };

  const generateAuthorityAlert = async () => {
    if (!simulation) return;
    setAuthorityAlert({ data: null, loading: true, error: null });
    try {
      setAuthorityAlert({ data: await api.aiAlert(simulation, "authority"), loading: false, error: null });
    } catch (err) {
      setAuthorityAlert({ data: null, loading: false, error: err instanceof Error ? err.message : "Alert failed" });
    }
  };

  const generateBrief = async () => {
    if (!simulation) return;
    setBrief({ data: null, loading: true, error: null });
    try {
      setBrief({ data: await api.aiStateBrief(simulation), loading: false, error: null });
    } catch (err) {
      setBrief({ data: null, loading: false, error: err instanceof Error ? err.message : "State brief failed" });
    }
  };

  return {
    simulation,
    running,
    runError,
    run,
    selectedZoneId,
    setSelectedZoneId,
    analysis,
    generateAnalysis,
    plan,
    generatePlan,
    citizenAlert,
    generateCitizenAlert,
    authorityAlert,
    generateAuthorityAlert,
    brief,
    generateBrief,
  };
}

export type RakshaSimulation = ReturnType<typeof useRakshaSimulation>;