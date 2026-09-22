"use client";

import ActionPlanPanel from "@/components/ActionPlanPanel";
import AlertsPanel from "@/components/AlertsPanel";
import AIAnalysisPanel from "@/components/AIAnalysisPanel";
import Disclaimer from "@/components/Disclaimer";
import Header from "@/components/Header";
import InfrastructurePanel from "@/components/InfrastructurePanel";
import RiskBreakdown from "@/components/RiskBreakdown";
import RiskMap from "@/components/RiskMap";
import RiskOverview from "@/components/RiskOverview";
import ScenarioForm from "@/components/ScenarioForm";
import StateBriefPanel from "@/components/StateBriefPanel";
import WhyRisk from "@/components/WhyRisk";
import { Badge, Card, EmptyState, ErrorBox } from "@/components/ui";
import { useRakshaSimulation } from "@/features/simulation/useSimulation";

const SECTIONS = [
  { id: "scenario", label: "Scenario" },
  { id: "map", label: "Risk Map" },
  { id: "breakdown", label: "Risk Breakdown" },
  { id: "infrastructure", label: "Critical Infrastructure" },
  { id: "ai", label: "AI Analysis" },
  { id: "plan", label: "Action Plan" },
  { id: "alerts", label: "Multilingual Alerts" },
  { id: "brief", label: "State Brief" },
];

export default function Page() {
  const sim = useRakshaSimulation();
  const simulation = sim.simulation;

  return (
    <div className="flex min-h-screen flex-col bg-slate-100">
      <Header />

      <main className="mx-auto w-full max-w-[1400px] flex-1 px-5 py-6">
        {/* Section navigation */}
        <nav className="mb-5 flex flex-wrap gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs shadow-sm">
          {SECTIONS.map((s) => (
            <a
              key={s.id}
              href={`#${s.id}`}
              className="rounded px-2 py-1 font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-500"
            >
              {s.label}
            </a>
          ))}
        </nav>

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-[340px,1fr]">
          {/* Left column: scenario */}
          <aside id="scenario" className="lg:sticky lg:top-5 lg:self-start">
            <Card title="Disaster Scenario" subtitle="Configure the scenario inputs">
              <ScenarioForm onRun={sim.run} running={sim.running} inlineError={sim.runError} />
            </Card>
          </aside>

          {/* Right column: results */}
          <div className="space-y-5">
            {!simulation && !sim.running && (
              <EmptyState
                title="No simulation yet"
                hint="Select a disaster type and location, then press Run Simulation to start the full intelligence flow."
              />
            )}
            {sim.running && (
              <Card>
                <p className="text-sm text-slate-600">
                  Running simulation: computing risk components, zones and infrastructure exposure…
                </p>
              </Card>
            )}

            {simulation && (
              <>
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <Badge tone="amber">DEMO DATA</Badge>
                  <Badge tone="blue">{simulation.scenario.severity} severity</Badge>
                  <Badge tone="slate">{simulation.scenario.disasterType}</Badge>
                  <Badge tone="slate">{simulation.scenario.sourceLabel}</Badge>
                  <span className="ml-auto text-slate-500">
                    {simulation.scenario.district}, {simulation.scenario.state}
                  </span>
                </div>

                <RiskOverview simulation={simulation} />

                <section id="map" className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                  <h3 className="mb-3 text-base font-semibold text-slate-900">Risk Map</h3>
                  <RiskMap
                    scenario={simulation.scenario}
                    zones={simulation.zones}
                    infrastructure={simulation.infrastructure.items}
                    selectedZoneId={sim.selectedZoneId}
                    onSelectZone={sim.setSelectedZoneId}
                    mapProvider={String(simulation.geoProvider.provider ?? "")}
                  />
                </section>

                <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
                  <section id="breakdown">
                    <RiskBreakdown risk={simulation.risk} />
                  </section>
                  <WhyRisk zones={simulation.zones} selectedZoneId={sim.selectedZoneId} />
                </div>

                <section id="infrastructure">
                  <InfrastructurePanel set={simulation.infrastructure} />
                </section>

                <section id="ai">
                  <AIAnalysisPanel
                    analysis={sim.analysis.data}
                    loading={sim.analysis.loading}
                    error={sim.analysis.error}
                    onGenerate={() => void sim.generateAnalysis()}
                  />
                </section>

                <section id="plan">
                  <ActionPlanPanel
                    plan={sim.plan.data}
                    loading={sim.plan.loading}
                    error={sim.plan.error}
                    onGenerate={() => void sim.generatePlan()}
                  />
                </section>

                <section id="alerts">
                  <AlertsPanel
                    citizen={sim.citizenAlert.data}
                    authority={sim.authorityAlert.data}
                    loading={sim.citizenAlert.loading}
                    loadingAuthority={sim.authorityAlert.loading}
                    error={sim.citizenAlert.error ?? sim.authorityAlert.error}
                    onGenerateCitizen={() => void sim.generateCitizenAlert()}
                    onGenerateAuthority={() => void sim.generateAuthorityAlert()}
                  />
                </section>

                <section id="brief">
                  <StateBriefPanel
                    brief={sim.brief.data}
                    loading={sim.brief.loading}
                    error={sim.brief.error}
                    onGenerate={() => void sim.generateBrief()}
                  />
                </section>
              </>
            )}

            {sim.runError && <ErrorBox message={sim.runError} />}
          </div>
        </div>
      </main>

      <Disclaimer />

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-[1400px] px-5 py-3 text-center text-xs text-slate-400">
          RakshaAI · Pre-Disaster Intelligence Prototype · Built for Build with AI: Code for Communities — Second Edition
        </div>
      </footer>
    </div>
  );
}