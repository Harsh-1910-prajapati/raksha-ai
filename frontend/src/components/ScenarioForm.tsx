"use client";

import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui";
import { api } from "@/lib/api";
import type { DisasterType, DisasterTypeConfig, District, ScenarioInput, State } from "@/lib/types";

const DEMO_SCENARIOS: Record<string, Partial<ScenarioInput>> = {
  CYCLONE: {
    disasterType: "CYCLONE",
    windSpeed: 140,
    rainfall: 220,
    stormSurge: 2.5,
    impactRadius: 80,
    durationHours: 12,
    populationExposure: 0,
  },
  FLOOD: {
    disasterType: "FLOOD",
    windSpeed: 0,
    rainfall: 180,
    stormSurge: 0.5,
    impactRadius: 60,
    durationHours: 24,
    populationExposure: 0,
  },
  EXTREME_RAINFALL: {
    disasterType: "EXTREME_RAINFALL",
    windSpeed: 0,
    rainfall: 320,
    stormSurge: 0,
    impactRadius: 40,
    durationHours: 8,
    populationExposure: 0,
  },
};

function Field({
  label,
  unit,
  children,
}: {
  label: string;
  unit?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 flex items-center justify-between text-xs font-medium text-slate-600">
        {label}
        {unit && <span className="text-[10px] uppercase text-slate-400">{unit}</span>}
      </span>
      {children}
    </label>
  );
}

const inputClass =
  "w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500";

export default function ScenarioForm({
  onRun,
  running,
  inlineError,
}: {
  onRun: (input: ScenarioInput) => Promise<unknown> | void;
  running: boolean;
  inlineError: string | null;
}) {
  const [disasterTypes, setDisasterTypes] = useState<DisasterTypeConfig[]>([]);
  const [states, setStates] = useState<State[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [disasterType, setDisasterType] = useState<DisasterType>("CYCLONE");
  const [state, setState] = useState("");
  const [district, setDistrict] = useState("");
  const [lat, setLat] = useState(17.6868);
  const [lon, setLon] = useState(83.2185);
  const [wind, setWind] = useState(140);
  const [rain, setRain] = useState(220);
  const [surge, setSurge] = useState(2.5);
  const [radius, setRadius] = useState(80);
  const [duration, setDuration] = useState(12);
  const [popOverride, setPopOverride] = useState(0);

  useEffect(() => {
    let mounted = true;
    Promise.all([api.disasterTypes(), api.states()])
      .then(([dt, st]) => {
        if (!mounted) return;
        setDisasterTypes(dt.disasterTypes);
        setStates(st.states);
        const first = st.states[0];
        if (first) {
          setState(first.name);
          api
            .districts(first.name)
            .then((d) => {
              if (!mounted) return;
              setDistricts(d.districts);
              const fd = d.districts[0];
              if (fd) {
                setDistrict(fd.name);
                setLat(fd.latitude);
                setLon(fd.longitude);
              }
            })
            .catch(() => mounted && setLoadError("Could not load districts."));
        }
      })
      .catch(() => mounted && setLoadError("Could not load location data. Is the backend running?"));
    return () => {
      mounted = false;
    };
  }, []);

  const currentConfig = useMemo(
    () => disasterTypes.find((d) => d.id === disasterType),
    [disasterTypes, disasterType]
  );

  function applyDisasterType(id: DisasterType) {
    setDisasterType(id);
    const cfg = disasterTypes.find((d) => d.id === id);
    const demo = DEMO_SCENARIOS[id];
    if (cfg || demo) {
      setWind((demo?.windSpeed ?? cfg?.defaults.windSpeed ?? 0) as number);
      setRain((demo?.rainfall ?? cfg?.defaults.rainfall ?? 0) as number);
      setSurge((demo?.stormSurge ?? cfg?.defaults.stormSurge ?? 0) as number);
      setRadius((demo?.impactRadius ?? cfg?.defaults.impactRadius ?? 60) as number);
      setDuration((demo?.durationHours ?? cfg?.defaults.durationHours ?? 12) as number);
    }
  }

  function onChangeState(name: string) {
    setState(name);
    setDistrict("");
    api
      .districts(name)
      .then((d) => {
        setDistricts(d.districts);
        const fd = d.districts[0];
        if (fd) {
          setDistrict(fd.name);
          setLat(fd.latitude);
          setLon(fd.longitude);
        }
      })
      .catch(() => setLoadError("Could not load districts for this state."));
  }

  function onChangeDistrict(name: string) {
    setDistrict(name);
    const d = districts.find((x) => x.name === name);
    if (d) {
      setLat(d.latitude);
      setLon(d.longitude);
    }
  }

  function loadDemo() {
    applyDisasterType("CYCLONE");
    const ap = states.find((s) => s.name === "Andhra Pradesh");
    if (ap) onChangeState(ap.name);
  }

  function submit() {
    const input: ScenarioInput = {
      disasterType,
      state,
      district,
      latitude: lat,
      longitude: lon,
      windSpeed: wind,
      rainfall: rain,
      stormSurge: surge,
      impactRadius: radius,
      durationHours: duration,
      populationExposure: popOverride,
    };
    onRun(input);
  }

  return (
    <div className="space-y-4">
      <div>
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
          1. Disaster type & location
        </p>
        <div className="grid grid-cols-1 gap-3">
          <Field label="Disaster Type">
            <select
              className={inputClass}
              value={disasterType}
              onChange={(e) => applyDisasterType(e.target.value as DisasterType)}
              aria-label="Disaster type"
            >
              {disasterTypes.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="State">
              <select
                className={inputClass}
                value={state}
                onChange={(e) => onChangeState(e.target.value)}
                aria-label="State"
              >
                {!state && <option value="">Loading…</option>}
                {states.map((s) => (
                  <option key={s.id} value={s.name}>
                    {s.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="District">
              <select
                className={inputClass}
                value={district}
                onChange={(e) => onChangeDistrict(e.target.value)}
                aria-label="District"
              >
                {!district && <option value="">Loading…</option>}
                {districts.map((d) => (
                  <option key={d.id} value={d.name}>
                    {d.name}
                  </option>
                ))}
              </select>
            </Field>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Latitude" unit="WGS84">
              <input
                type="number"
                step="0.0001"
                min={-90}
                max={90}
                className={inputClass}
                value={lat}
                onChange={(e) => setLat(Number(e.target.value))}
              />
            </Field>
            <Field label="Longitude" unit="WGS84">
              <input
                type="number"
                step="0.0001"
                min={-180}
                max={180}
                className={inputClass}
                value={lon}
                onChange={(e) => setLon(Number(e.target.value))}
              />
            </Field>
          </div>
        </div>
      </div>

      <div>
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
          2. Scenario parameters
        </p>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Max Wind Speed" unit="km/h">
            <input
              type="number"
              min={0}
              className={inputClass}
              value={wind}
              onChange={(e) => setWind(Number(e.target.value))}
              disabled={disasterType !== "CYCLONE"}
            />
          </Field>
          <Field label="Rainfall" unit="mm">
            <input
              type="number"
              min={0}
              className={inputClass}
              value={rain}
              onChange={(e) => setRain(Number(e.target.value))}
            />
          </Field>
          <Field label="Storm Surge" unit="m">
            <input
              type="number"
              min={0}
              step="0.1"
              className={inputClass}
              value={surge}
              onChange={(e) => setSurge(Number(e.target.value))}
            />
          </Field>
          <Field label="Impact Radius" unit="km">
            <input
              type="number"
              min={1}
              className={inputClass}
              value={radius}
              onChange={(e) => setRadius(Number(e.target.value))}
            />
          </Field>
          <Field label="Duration" unit="hours">
            <input
              type="number"
              min={1}
              max={168}
              className={inputClass}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
            />
          </Field>
          <Field label="Population Override" unit="0 = estimate">
            <input
              type="number"
              min={0}
              className={inputClass}
              value={popOverride}
              onChange={(e) => setPopOverride(Number(e.target.value))}
            />
          </Field>
        </div>
      </div>

      {currentConfig && (
        <p className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-500">
          {currentConfig.description}
        </p>
      )}

      {loadError && (
        <p className="rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
          {loadError}
        </p>
      )}
      {inlineError && (
        <p className="rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
          {inlineError}
        </p>
      )}

      <div className="flex flex-col gap-2">
        <Button onClick={submit} disabled={running || !state || !district} className="w-full py-2.5 text-base">
          {running ? "Running simulation…" : "Run Simulation"}
        </Button>
        <Button onClick={loadDemo} variant="secondary" disabled={running} className="w-full">
          Load Demo Scenario
        </Button>
      </div>
    </div>
  );
}