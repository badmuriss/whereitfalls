import { Satellite } from "lucide-react";

import type { ReentrySummary, RiskRegion } from "../api/types";
import { useCountdown } from "../hooks/useCountdown";
import { formatUtc } from "../lib/format";
import { CONFIDENCE_LABEL, OBJECT_TYPE_LABEL } from "../lib/labels";
import { tierStyle } from "../lib/severity";

interface EventHeaderProps {
  event: ReentrySummary;
  leadRisk: RiskRegion | undefined;
}

/** Cabeçalho-história do evento focado: o quê, quando (countdown), onde (região líder). */
export function EventHeader({ event, leadRisk }: EventHeaderProps) {
  const countdown = useCountdown(event.predicted_reentry_utc);
  const tier = leadRisk ? tierStyle(leadRisk.score) : undefined;

  return (
    <header className="event-header" data-tier={tier?.tier ?? "monitor"}>
      <div className="event-header__top">
        <span className="eyebrow eyebrow--tier">
          <i className="pulse-dot" aria-hidden />
          {countdown.past ? "Janela de reentrada ativa" : "Próxima reentrada"}
        </span>
        <span className="event-header__meta">
          <Satellite size={14} strokeWidth={1.75} />
          {OBJECT_TYPE_LABEL[event.type]} · {event.country} · {CONFIDENCE_LABEL[event.confidence]}
        </span>
      </div>

      <div className="event-header__body">
        <div className="event-header__id">
          <h1>{event.name}</h1>
          <span className="event-header__norad">NORAD {event.norad_id}</span>
        </div>

        <div className="event-header__count">
          <span className="event-header__count-label">
            {countdown.past ? "Decorrido" : "Reentrada estimada em"}
          </span>
          <strong className="countdown">{countdown.label}</strong>
          <span className="event-header__window">
            {formatUtc(event.predicted_reentry_utc)} · janela ±{event.uncertainty_minutes} min
          </span>
        </div>
      </div>
    </header>
  );
}
