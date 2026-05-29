import { Activity, Radar, RadioTower, ShieldAlert } from "lucide-react";
import { Suspense, lazy, useEffect, useMemo, useState, type ReactNode } from "react";

import { getReentryDetail, getReentries, getRisk } from "./api/client";
import type { ReentryDetail, ReentrySummary, RiskRegion } from "./api/types";
import logoUrl from "./assets/whereitfalls-mark.svg";
import { EventHeader } from "./components/EventHeader";
import { EventSelector } from "./components/EventSelector";
import { ExposurePanel } from "./components/ExposurePanel";
import { StageToggle, type StageView } from "./components/StageToggle";
import { useNow } from "./hooks/useNow";
import { formatClockUtc } from "./lib/format";
import { scoreToIndex, tierStyle } from "./lib/severity";
import { ReentryMap } from "./map/ReentryMap";

const ReentryGlobe = lazy(() => import("./globe/ReentryGlobe"));

interface DashboardState {
  reentries: ReentrySummary[];
  risks: RiskRegion[];
  loading: boolean;
  error: string | null;
}

const initialState: DashboardState = { reentries: [], risks: [], loading: true, error: null };

function bestByKey(risks: RiskRegion[], key: (r: RiskRegion) => string): RiskRegion[] {
  const map = new Map<string, RiskRegion>();
  risks.forEach((r) => {
    const k = key(r);
    const current = map.get(k);
    if (!current || r.score > current.score) map.set(k, r);
  });
  return [...map.values()];
}

export function App() {
  const [state, setState] = useState<DashboardState>(initialState);
  const [focusedId, setFocusedId] = useState<string | undefined>(undefined);
  const [detail, setDetail] = useState<ReentryDetail | null>(null);
  // mapa 2D como padrão (leve); globo 3D é opt-in pelo toggle (three.js só carrega ao pedir)
  const [view, setView] = useState<StageView>("map");

  const now = useNow(1000);

  useEffect(() => {
    let active = true;
    Promise.all([getReentries(), getRisk()])
      .then(([reentries, risks]) => {
        if (!active) return;
        setState({ reentries: reentries.items, risks: risks.items, loading: false, error: null });
        setFocusedId((prev) => prev ?? reentries.items[0]?.prediction_id);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setState((c) => ({ ...c, loading: false, error: error instanceof Error ? error.message : "Falha ao carregar telemetria." }));
      });
    return () => {
      active = false;
    };
  }, []);

  const focusedEvent = useMemo(
    () => state.reentries.find((r) => r.prediction_id === focusedId) ?? state.reentries[0],
    [state.reentries, focusedId],
  );

  // detalhe (ground_track + corredor) do objeto focado
  useEffect(() => {
    if (!focusedEvent) return;
    let active = true;
    setDetail(null);
    getReentryDetail(focusedEvent.norad_id)
      .then((d) => active && setDetail(d))
      .catch(() => active && setDetail(null));
    return () => {
      active = false;
    };
    // refetch só quando muda o objeto (norad), não a cada nova identidade de focusedEvent
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focusedEvent?.norad_id]);

  const leadByPrediction = useMemo(() => {
    const map = new Map<string, RiskRegion>();
    state.risks.forEach((r) => {
      const c = map.get(r.prediction_id);
      if (!c || r.score > c.score) map.set(r.prediction_id, r);
    });
    return map;
  }, [state.risks]);

  const focusedRegions = useMemo(() => {
    if (!focusedEvent) return [];
    const scoped = state.risks.filter((r) => r.prediction_id === focusedEvent.prediction_id);
    return bestByKey(scoped, (r) => r.region).sort((a, b) => b.score - a.score);
  }, [state.risks, focusedEvent]);

  const contextRisks = useMemo(() => bestByKey(state.risks, (r) => r.region), [state.risks]);
  const leadRisk = focusedRegions[0];

  const maxScore = useMemo(() => contextRisks.reduce((m, r) => Math.max(m, r.score), 0), [contextRisks]);
  const criticalCount = useMemo(() => contextRisks.filter((r) => r.score >= 0.7).length, [contextRisks]);


  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar__brand">
          <img src={logoUrl} alt="" aria-hidden />
          <strong>WhereItFalls</strong>
          <span className="topbar__tag">Alerta de reentrada</span>
        </div>
        <div className="topbar__right">
          <span className="topbar__clock">{formatClockUtc(new Date(now))}</span>
          <span className="topbar__source">
            <i className="status-dot" aria-hidden />
            Space-Track · ao vivo
          </span>
        </div>
      </header>

      <div className="layout">
        <aside className="rail rail--left" aria-label="Contexto global e seleção de evento">
          <section className="summary">
            <Stat icon={<Activity size={16} strokeWidth={1.75} />} label="Objetos monitorados" value={state.reentries.length} />
            <Stat
              icon={<ShieldAlert size={16} strokeWidth={1.75} />}
              label="Índice máximo global"
              value={scoreToIndex(maxScore)}
              tier={maxScore ? tierStyle(maxScore).tier : undefined}
            />
            <Stat icon={<Radar size={16} strokeWidth={1.75} />} label="Regiões críticas" value={criticalCount} tier={criticalCount ? "critical" : undefined} />
          </section>

          <section className="panel selector-panel">
            <div className="panel__head">
              <RadioTower size={15} strokeWidth={1.75} />
              <span>Reentradas monitoradas</span>
            </div>
            {state.loading ? (
              <Skeleton rows={5} />
            ) : (
              <EventSelector
                reentries={state.reentries}
                focusedPredictionId={focusedEvent?.prediction_id}
                leadByPrediction={leadByPrediction}
                onFocus={setFocusedId}
              />
            )}
          </section>
        </aside>

        <main className="stage" aria-label="Evento focado">
          {state.error ? <div className="error-banner">{state.error}</div> : null}
          {focusedEvent ? (
            <div className="stage__head">
              <EventHeader event={focusedEvent} leadRisk={leadRisk} />
              <StageToggle value={view} onChange={setView} />
            </div>
          ) : null}

          <div className="stage__view">
            {view === "globe" ? (
              <Suspense fallback={<div className="stage__fallback">Carregando globo 3D…</div>}>
                <ReentryGlobe focusedDetail={detail} focusedRegions={focusedRegions} />
              </Suspense>
            ) : (
              <ReentryMap
                contextRisks={contextRisks}
                focusedRegions={focusedRegions}
                focusedDetail={detail}
                loading={state.loading}
              />
            )}
          </div>

          <Legend />
        </main>

        <aside className="rail rail--right" aria-label="Exposição no solo">
          <section className="panel">
            <div className="panel__head">
              <ShieldAlert size={15} strokeWidth={1.75} />
              <span>Exposição no solo</span>
            </div>
            {state.loading ? <Skeleton rows={4} /> : <ExposurePanel regions={focusedRegions} />}
          </section>
        </aside>
      </div>
    </div>
  );
}

function Stat({
  icon,
  label,
  value,
  tier,
}: {
  icon: ReactNode;
  label: string;
  value: string | number;
  tier?: string;
}) {
  return (
    <div className="stat" data-tier={tier}>
      <span className="stat__icon">{icon}</span>
      <strong className="stat__value">{value}</strong>
      <span className="stat__label">{label}</span>
    </div>
  );
}

const LEGEND: Array<{ tier: string; label: string }> = [
  { tier: "monitor", label: "Monitorar" },
  { tier: "attention", label: "Atenção" },
  { tier: "elevated", label: "Elevado" },
  { tier: "critical", label: "Crítico" },
];

function Legend() {
  return (
    <div className="legend" aria-label="Legenda de severidade">
      {LEGEND.map((l) => (
        <span key={l.tier} data-tier={l.tier}>
          <i className="tier-dot" aria-hidden />
          {l.label}
        </span>
      ))}
      <span className="legend__scale">índice 0–100 · proximidade × exposição</span>
    </div>
  );
}

function Skeleton({ rows }: { rows: number }) {
  return (
    <div className="skeleton" aria-hidden>
      {Array.from({ length: rows }).map((_, i) => (
        <span key={i} />
      ))}
    </div>
  );
}
