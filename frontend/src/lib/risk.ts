import type { RiskLevel } from "./types";

export const RISK_LEVELS: RiskLevel[] = ["LOW", "MODERATE", "HIGH", "CRITICAL"];

export const RISK_STYLES: Record<
  RiskLevel,
  { bg: string; text: string; border: string; hex: string; description: string }
> = {
  LOW: {
    bg: "bg-emerald-100",
    text: "text-emerald-800",
    border: "border-emerald-300",
    hex: "#d1fae5",
    description: "Limited expected impact",
  },
  MODERATE: {
    bg: "bg-amber-100",
    text: "text-amber-800",
    border: "border-amber-300",
    hex: "#fef3c7",
    description: "Notable expected impact",
  },
  HIGH: {
    bg: "bg-orange-100",
    text: "text-orange-800",
    border: "border-orange-300",
    hex: "#ffe4cc",
    description: "Severe expected impact",
  },
  CRITICAL: {
    bg: "bg-red-100",
    text: "text-red-800",
    border: "border-red-300",
    hex: "#fee2e2",
    description: "Extreme expected impact",
  },
};

export const RISK_STROKE: Record<RiskLevel, string> = {
  LOW: "#10b981",
  MODERATE: "#f59e0b",
  HIGH: "#f97316",
  CRITICAL: "#dc2626",
};

export const RISK_FILL: Record<RiskLevel, string> = {
  LOW: "rgba(16,185,129,0.25)",
  MODERATE: "rgba(245,158,11,0.3)",
  HIGH: "rgba(249,115,22,0.35)",
  CRITICAL: "rgba(220,38,38,0.4)",
};

export const RISK_RANK: Record<RiskLevel, number> = {
  LOW: 0,
  MODERATE: 1,
  HIGH: 2,
  CRITICAL: 3,
};

export const levelOf = (score: number): RiskLevel => {
  if (score >= 76) return "CRITICAL";
  if (score >= 51) return "HIGH";
  if (score >= 26) return "MODERATE";
  return "LOW";
};

export const formatPopulation = (n: number): string => {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${Math.round(n / 1_000)}K`;
  return `${n}`;
};

export const INFRA_LABEL: Record<string, string> = {
  hospital: "Hospital",
  shelter: "Emergency Shelter",
  road: "Road",
  bridge: "Bridge",
  power: "Power Station",
  water: "Water Facility",
  school: "School",
  police: "Police Station",
  fire: "Fire Station",
};