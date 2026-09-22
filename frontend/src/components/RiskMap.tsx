"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */

import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import { INFRA_LABEL, RISK_LEVELS } from "@/lib/risk";
import type { InfrastructureItem, Scenario, ZoneRisk } from "@/lib/types";

interface Proj {
  x: number;
  y: number;
}

interface RiskMapProps {
  scenario: Scenario;
  zones: ZoneRisk[];
  infrastructure: InfrastructureItem[];
  selectedZoneId?: string | null;
  onSelectZone?: (id: string) => void;
  mapProvider?: string;
}

const ZONE_COLOR: Record<string, string> = {
  LOW: "#10b981",
  MODERATE: "#f59e0b",
  HIGH: "#f97316",
  CRITICAL: "#dc2626",
};

const INFRA_COLORS: Partial<Record<string, string>> = {
  hospital: "#dc2626",
  shelter: "#059669",
  power: "#d97706",
  water: "#0284c7",
  school: "#7c3aed",
  police: "#334155",
  fire: "#ea580c",
  bridge: "#475569",
  road: "#94a3b8",
};

const MAP_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY?.trim() || "";

export default function RiskMap(props: RiskMapProps) {
  const [mode, setMode] = useState<"google" | "svg">(MAP_KEY ? "google" : "svg");

  if (mode === "google") {
    return (
      <div>
        <GoogleMap
          {...props}
          selectedZoneId={props.selectedZoneId ?? null}
          onSelectZone={(id) => props.onSelectZone?.(id)}
          onFail={() => setMode("svg")}
        />
      </div>
    );
  }
  return <SvgRiskMap {...props} />;
}

// ---------------------------------------------------------------------------
// Google Maps (optional). Activates only when NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
// is set. Any failure falls back to the built-in SVG map.
// ---------------------------------------------------------------------------

type GoogleWindow = Window & { google?: { maps?: unknown }; __rakshaMapsLoader?: Promise<any> };

function GoogleMap({
  scenario,
  zones,
  infrastructure,
  selectedZoneId,
  onSelectZone,
  onFail,
  mapProvider,
}: {
  scenario: Scenario;
  zones: ZoneRisk[];
  infrastructure: InfrastructureItem[];
  selectedZoneId: string | null;
  onSelectZone: (id: string) => void;
  onFail: () => void;
  mapProvider?: string;
}) {
  const hostRef = useRef<HTMLDivElement>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    const win = window as GoogleWindow;
    let cancelled = false;
    let map: any;
    const markers: any[] = [];
    let circle: any;

    function render(google: any) {
      if (!hostRef.current || cancelled) return;
      const center = { lat: scenario.latitude, lng: scenario.longitude };
      map = new google.maps.Map(hostRef.current, {
        center,
        zoom: 9,
        mapTypeId: "terrain",
        fullscreenControl: true,
        mapTypeControl: false,
        streetViewControl: false,
      });

      const radiusM = scenario.impactRadius * 1000;
      circle = new google.maps.Circle({
        strokeColor: "#0f172a",
        strokeOpacity: 0.7,
        strokeWeight: 1,
        fillColor: "rgba(15,23,42,0.08)",
        fillOpacity: 1,
        map,
        center,
        radius: radiusM,
      });

      zones.forEach((z) => {
        const m = new google.maps.Marker({
          position: { lat: z.latitude, lng: z.longitude },
          map,
          title: `${z.label} — ${z.riskScore}/100 ${z.riskLevel}`,
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: selectedZoneId === z.id ? 9 : 7,
            fillColor: ZONE_COLOR[z.riskLevel],
            fillOpacity: 0.85,
            strokeColor: "#0f172a",
            strokeWeight: 1,
          },
        });
        m.addListener("click", () => onSelectZone(z.id));
        markers.push(m);
      });

      infrastructure.forEach((it) => {
        if (it.geometry === "line" && it.path) {
          const path = it.path.map(([la, lo]) => ({ lat: la, lng: lo }));
          new google.maps.Polyline({
            path,
            map,
            strokeColor: ZONE_COLOR[it.riskLevel] ?? "#94a3b8",
            strokeWeight: 3,
          });
          return;
        }
        const m = new google.maps.Marker({
          position: { lat: it.latitude, lng: it.longitude },
          map,
          title: `${it.name} (${it.riskScore}/100 ${it.riskLevel})`,
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 5,
            fillColor: "#ffffff",
            fillOpacity: 1,
            strokeColor: INFRA_COLORS[it.type] ?? "#94a3b8",
            strokeWeight: 2,
          },
        });
        markers.push(m);
      });
    }

    function loadGoogle(): Promise<any> {
      if (win.__rakshaMapsLoader) return win.__rakshaMapsLoader;
      win.__rakshaMapsLoader = new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = `https://maps.googleapis.com/maps/api/js?key=${MAP_KEY}&callback=__rakshaInit&libraries=geometry`;
        const cb = () => resolve(win.google?.maps);
        (win as any).__rakshaInit = cb;
        window.addEventListener("error", function onErr(err) {
          if (err.message?.includes("maps.googleapis")) {
            window.removeEventListener("error", onErr);
            reject(new Error("Google Maps script failed to load"));
          }
        });
        script.onerror = () => reject(new Error("Google Maps script failed to load"));
        document.head.appendChild(script);
        setTimeout(() => reject(new Error("Google Maps load timed out")), 15000);
      });
      return win.__rakshaMapsLoader;
    }

    loadGoogle()
      .then((google) => {
        if (cancelled) return;
        render(google);
      })
      .catch((err) => {
        if (!cancelled) {
          setLoadError((err as Error).message);
          onFail();
        }
      });

    return () => {
      cancelled = true;
      markers.forEach((m) => m?.setMap?.(null));
      circle?.setMap?.(null);
      map?.setMap?.({} as any);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loadError) {
    return (
      <p className="mb-2 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
        Google Maps could not load ({loadError || "unknown error"}). Using the built-in map.
      </p>
    );
  }
  return (
    <div className="mb-2">
      <p className="mb-2 text-[11px] text-slate-500">
        Live Google Maps view (NEXT_PUBLIC_GOOGLE_MAPS_API_KEY configured)
        {mapProvider ? ` · map data: ${mapProvider}` : ""}.
      </p>
      <div ref={hostRef} className="h-[420px] w-full rounded-md border border-slate-200" />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Built-in offline SVG map (always works)
// ---------------------------------------------------------------------------

function project(
  lat: number,
  lon: number,
  centerLat: number,
  centerLon: number,
  spanKm: number,
  w: number,
  h: number,
  pad: number
): Proj {
  const dLat = spanKm / 110.574;
  const dLon = spanKm / (111.32 * Math.max(Math.cos((centerLat * Math.PI) / 180), 0.2));
  const x = ((lon - (centerLon - dLon)) / (2 * dLon)) * (w - 2 * pad) + pad;
  const y = ((centerLat + dLat - lat) / (2 * dLat)) * (h - 2 * pad) + pad;
  return { x, y };
}

function SvgRiskMap({
  scenario,
  zones,
  infrastructure,
  selectedZoneId,
  onSelectZone,
  mapProvider,
}: RiskMapProps) {
  const W = 900;
  const H = 560;
  const PAD = 46;
  const spanKm = Math.max(scenario.impactRadius * 2.2, 20);

  const positions = useMemo(() => {
    const center = project(scenario.latitude, scenario.longitude, scenario.latitude, scenario.longitude, spanKm, W, H, PAD);
    const byId: Record<string, { zone?: Proj; roadWays?: [Proj, Proj][] }> = {};
    zones.forEach((z) => {
      byId[`zone:${z.id}`] = {
        zone: project(z.latitude, z.longitude, scenario.latitude, scenario.longitude, spanKm, W, H, PAD),
      };
    });
    infrastructure.forEach((it) => {
      const pts = it.path && it.path.length ? it.path : [[it.latitude, it.longitude]];
      const waypoints = pts.map(([la, lo]) =>
        project(la, lo, scenario.latitude, scenario.longitude, spanKm, W, H, PAD)
      );
      const ways: [Proj, Proj][] = [];
      for (let i = 0; i < waypoints.length - 1; i++) ways.push([waypoints[i], waypoints[i + 1]]);
      byId[`infra:${it.id}`] = { roadWays: ways.length ? ways : undefined, zone: waypoints[waypoints.length - 1] };
    });
    return { center, byId };
  }, [scenario, zones, infrastructure, spanKm]);

  const ringSizes = [0.25, 0.5, 0.75, 1.0];

  return (
    <div>
      <p className="mb-2 flex items-center gap-2 text-[11px] text-slate-500">
        <span className="inline-block h-2 w-2 rounded-full bg-slate-300" />
        Offline risk map (built-in). Add NEXT_PUBLIC_GOOGLE_MAPS_API_KEY for live Google Maps.
      </p>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full rounded-md border border-slate-200 bg-[#eef1f4]"
        role="img"
        aria-label="Risk map for the disaster scenario"
      >
        <defs>
          <clipPath id="map-clip">
            <rect x={PAD - 8} y={PAD - 8} width={W - 2 * PAD + 16} height={H - 2 * PAD + 16} rx={6} />
          </clipPath>
        </defs>

        <g clipPath="url(#map-clip)">
          {Array.from({ length: 7 }).map((_, i) => {
            const t = (i + 1) / 8;
            return (
              <Fragment key={`g${i}`}>
                <line x1={PAD + t * (W - 2 * PAD)} y1={PAD} x2={PAD + t * (W - 2 * PAD)} y2={H - PAD} stroke="#d7dde3" strokeWidth="1" />
                <line x1={PAD} y1={PAD + t * (H - 2 * PAD)} x2={W - PAD} y2={PAD + t * (H - 2 * PAD)} stroke="#d7dde3" strokeWidth="1" />
              </Fragment>
            );
          })}

          {ringSizes.map((f) => {
            const r = Math.max(f * ((Math.min(W, H) - 2 * PAD) / 2), 2);
            return (
              <g key={`ring${f}`}>
                <circle
                  cx={positions.center.x}
                  cy={positions.center.y}
                  r={r}
                  fill={f === 1 ? "rgba(148,163,184,0.12)" : "none"}
                  stroke="#94a3b8"
                  strokeWidth="1"
                  strokeDasharray={f === 1 ? "none" : "4 4"}
                />
                <text x={positions.center.x + r + 4} y={positions.center.y - 4} fontSize="10" fill="#64748b">
                  {Math.round(scenario.impactRadius * f)} km
                </text>
              </g>
            );
          })}

          {infrastructure
            .filter((i) => i.geometry === "line")
            .map((it) => {
              const entry = positions.byId[`infra:${it.id}`];
              if (!entry?.roadWays) return null;
              const color = ZONE_COLOR[it.riskLevel] ?? INFRA_COLORS[it.type] ?? "#94a3b8";
              return (
                <g key={it.id}>
                  {entry.roadWays.map(([a, b], idx) => (
                    <line
                      key={idx}
                      x1={a.x}
                      y1={a.y}
                      x2={b.x}
                      y2={b.y}
                      stroke={color}
                      strokeWidth={2.5}
                      strokeLinecap="round"
                      opacity={0.85}
                    />
                  ))}
                </g>
              );
            })}

          {zones.map((z) => {
            const pos = positions.byId[`zone:${z.id}`];
            if (!pos?.zone) return null;
            const selected = selectedZoneId === z.id;
            return (
              <g key={z.id} onClick={() => onSelectZone?.(z.id)} className="cursor-pointer">
                <circle
                  cx={pos.zone.x}
                  cy={pos.zone.y}
                  r={selected ? 9 : 7}
                  fill={ZONE_COLOR[z.riskLevel]}
                  fillOpacity={z.riskLevel === "LOW" ? 0.5 : 0.85}
                  stroke="#0f172a"
                  strokeWidth={selected ? 2.5 : 1}
                />
                <title>{`${z.label} — ${z.riskScore}/100 ${z.riskLevel}`}</title>
              </g>
            );
          })}

          {infrastructure
            .filter((i) => i.geometry !== "line")
            .map((it) => {
              const pos = positions.byId[`infra:${it.id}`];
              if (!pos?.zone) return null;
              return (
                <g key={it.id}>
                  <circle cx={pos.zone.x} cy={pos.zone.y} r={5} fill="#ffffff" stroke={INFRA_COLORS[it.type] ?? "#94a3b8"} strokeWidth={2} />
                  <circle cx={pos.zone.x} cy={pos.zone.y} r={2} fill="#334155" />
                  <title>{`${it.name} (${INFRA_LABEL[it.type] ?? it.type}) — ${it.riskScore}/100 ${it.riskLevel}`}</title>
                </g>
              );
            })}

          <g>
            <circle cx={positions.center.x} cy={positions.center.y} r={8} fill="#0f172a" fillOpacity="0.15" />
            <circle cx={positions.center.x} cy={positions.center.y} r={4} fill="#0f172a" />
            <text x={positions.center.x + 10} y={positions.center.y - 10} fontSize="11" fontWeight="600" fill="#0f172a">
              Scenario Centre
            </text>
            <text x={positions.center.x + 10} y={positions.center.y + 4} fontSize="10" fill="#475569">
              {scenario.latitude.toFixed(3)}, {scenario.longitude.toFixed(3)}
            </text>
          </g>
        </g>
      </svg>

      <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-slate-600">
        <span className="font-semibold text-slate-700">Risk Level</span>
        {RISK_LEVELS.map((lvl) => (
          <span key={lvl} className="inline-flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-full" style={{ background: ZONE_COLOR[lvl] }} />
            {lvl}
          </span>
        ))}
        <span className="inline-flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-full border-2 border-slate-700 bg-white" />
          Infrastructure
        </span>
        <span className="text-[11px] text-slate-400">
          Map data: {mapProvider ? `${mapProvider} (demo)` : "demo"}
        </span>
      </div>
    </div>
  );
}