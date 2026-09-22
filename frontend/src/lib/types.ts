// TypeScript types mirroring the RakshaAI backend API.

export type DisasterType = "CYCLONE" | "FLOOD" | "EXTREME_RAINFALL";
export type RiskLevel = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";

export interface DisasterTypeConfig {
  id: DisasterType;
  name: string;
  description: string;
  defaults: {
    windSpeed: number;
    rainfall: number;
    stormSurge: number;
    impactRadius: number;
    durationHours: number;
  };
  windSpeedUnit: string;
  rainfallUnit: string;
  stormSurgeUnit: string;
  radiusUnit: string;
}

export interface State {
  id: string;
  name: string;
  coastal: boolean;
}

export interface District {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
}

export interface ScenarioInput {
  disasterType: DisasterType;
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  windSpeed: number;
  rainfall: number;
  stormSurge: number;
  impactRadius: number;
  durationHours: number;
  populationExposure: number;
}

export interface Scenario {
  id: string;
  disasterType: DisasterType;
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  windSpeed: number;
  rainfall: number;
  stormSurge: number;
  impactRadius: number;
  durationHours: number;
  populationExposure: number;
  severity: string;
  createdAt: string;
  sourceLabel: string;
}

export interface RiskComponent {
  name: string;
  score: number;
  level: RiskLevel;
  factors: string[];
  weight: number;
}

export interface RiskResult {
  disasterType: string;
  state: string;
  district: string;
  overall: {
    score: number;
    level: RiskLevel;
    weights: Record<string, number>;
    label: string;
    weightsNote: string;
  };
  components: Record<string, RiskComponent>;
  exposure: Exposure;
  zones: ZoneRisk[];
  inferenceNote: string;
}

export interface Exposure {
  populationExposed: number;
  populationRiskScore: number;
  areaSqKm: number;
  severityLabel: string;
  sourcesNote: string;
}

export interface ZoneRisk {
  id: string;
  label: string;
  latitude: number;
  longitude: number;
  distanceKm: number;
  elevationM: number;
  riskScore: number;
  riskLevel: RiskLevel;
  components: Record<string, number>;
  factors: string[];
}

export interface HighRiskArea {
  label: string;
  latitude: number;
  longitude: number;
  riskScore: number;
  riskLevel: RiskLevel;
  factors: string[];
}

export type InfraType =
  | "hospital"
  | "shelter"
  | "road"
  | "bridge"
  | "power"
  | "water"
  | "school"
  | "police"
  | "fire";

export interface InfrastructureItem {
  id: string;
  name: string;
  type: InfraType;
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  capacity?: number | null;
  riskScore: number;
  riskLevel: RiskLevel;
  threats: string[];
  recommendation: string;
  priority: number;
  geometry: "point" | "line";
  path?: [number, number][] | null;
  sourceLabel: string;
}

export interface InfrastructureSet {
  state: string;
  district: string;
  scenarioLatitude: number;
  scenarioLongitude: number;
  items: InfrastructureItem[];
  counts: Record<string, number>;
  note: string;
}

export interface Simulation {
  disasterType: DisasterType;
  state: string;
  district: string;
  scenario: Scenario;
  risk: RiskResult;
  zones: ZoneRisk[];
  highRiskAreas: HighRiskArea[];
  infrastructure: InfrastructureSet;
  exposure: Exposure;
  geoProvider: Record<string, unknown>;
  infraProvider: Record<string, unknown>;
}

export interface AIAnalysis {
  ai_provider: "gemini" | "mock";
  provider_note: string;
  summary: string;
  priorityAreas: string[];
  infrastructureRisks: string[];
  recommendedActions: string[];
  resourcePriorities: string[];
  evacuationConsiderations: string[];
  communicationGuidance: string[];
}

export interface ActionPlan {
  ai_provider: "gemini" | "mock";
  provider_note: string;
  immediateActions: string[];
  beforeImpact: string[];
  duringEvent: string[];
  recovery: string[];
}

export interface AlertLang {
  language: "en" | "hi" | "te";
  language_name: string;
  title: string;
  body: string;
}

export interface AlertContent {
  ai_provider: "gemini" | "mock";
  provider_note: string;
  alert_type: "authority" | "citizen";
  title: string;
  summary: string;
  languages: AlertLang[];
  disclaimer: string;
}

export interface StateBrief {
  ai_provider: "gemini" | "mock";
  provider_note: string;
  state: string;
  generatedAt: string;
  affectedDistricts: string[];
  highRiskZones: string[];
  criticalInfrastructure: Record<string, number>;
  hospitalsAtRisk: string[];
  sheltersAtRisk: string[];
  accessibilityIssues: string[];
  recommendedPriorities: string[];
  communicationMessage: string;
  disclaimer: string;
}