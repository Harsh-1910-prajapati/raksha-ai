// Thin API client for the RakshaAI backend.
// Falls back gracefully: every method throws a descriptive Error that the UI
// surfaces rather than crashing.

import type {
  AIAnalysis,
  ActionPlan,
  AlertContent,
  DisasterTypeConfig,
  District,
  ScenarioInput,
  Simulation,
  State,
  StateBrief,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status = 0) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let controller: AbortController | undefined;
  if (typeof AbortController !== "undefined") {
    controller = new AbortController();
    const timer = setTimeout(() => controller?.abort(), 30_000);
    init = { ...init, signal: controller.signal };
    init.signal?.addEventListener("abort", () => clearTimeout(timer));
  }
  try {
    const res = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: init?.body
        ? { "Content-Type": "application/json", ...(init.headers ?? {}) }
        : init?.headers,
    });
    if (!res.ok) {
      let detail = `Backend returned ${res.status}`;
      try {
        const body = await res.json();
        if (body?.detail) {
          if (typeof body.detail === "string") detail = body.detail;
          else if (Array.isArray(body.detail)) {
            detail = body.detail
              .map((d: { msg?: string }) => d.msg ?? JSON.stringify(d))
              .join("; ");
          }
        }
      } catch {
        /* ignore body parse failure */
      }
      throw new ApiError(detail, res.status);
    }
    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err instanceof Error && err.name === "AbortError") {
      throw new ApiError("Request timed out. Is the backend running?", 0);
    }
    throw new ApiError(
      `Cannot reach the RakshaAI backend at ${API_URL}. Start it with \`uvicorn app.main:app --reload\` (from backend/) and check NEXT_PUBLIC_API_URL if it points elsewhere.`,
      0
    );
  }
}

export const api = {
  health: () => request<Record<string, unknown>>("/health"),

  states: () =>
    request<{ states: State[]; sourceLabel: string }>("/api/locations/states"),
  districts: (state: string) =>
    request<{ state: string; districts: District[]; sourceLabel: string }>(
      `/api/locations/${encodeURIComponent(state)}/districts`
    ),
  disasterTypes: () =>
    request<{ disasterTypes: DisasterTypeConfig[] }>("/api/locations/disaster-types"),

  simulate: (input: ScenarioInput) =>
    request<Simulation>("/api/scenarios/simulate", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  aiAnalyze: (simulation: Simulation) =>
    request<AIAnalysis>("/api/ai/analyze", {
      method: "POST",
      body: JSON.stringify({ simulation }),
    }),
  aiActionPlan: (simulation: Simulation) =>
    request<ActionPlan>("/api/ai/action-plan", {
      method: "POST",
      body: JSON.stringify({ simulation }),
    }),
  aiAlert: (simulation: Simulation, alertType: "citizen" | "authority") =>
    request<AlertContent>("/api/ai/alert", {
      method: "POST",
      body: JSON.stringify({ simulation, alertType }),
    }),
  aiStateBrief: (simulation: Simulation) =>
    request<StateBrief>("/api/ai/state-brief", {
      method: "POST",
      body: JSON.stringify({ simulation }),
    }),
};

export { API_URL };