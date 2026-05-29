import type { ReentrySummary, RiskRegion } from "../api/types";
import { formatUtc } from "../lib/format";
import { scoreToIndex, tierStyle } from "../lib/severity";

interface EventSelectorProps {
  reentries: ReentrySummary[];
  focusedPredictionId: string | undefined;
  leadByPrediction: Map<string, RiskRegion>;
  onFocus: (predictionId: string) => void;
}

/** Lista de reentradas monitoradas — clicar foca o evento em todo o painel. */
export function EventSelector({
  reentries,
  focusedPredictionId,
  leadByPrediction,
  onFocus,
}: EventSelectorProps) {
  return (
    <ul className="event-list" aria-label="Reentradas monitoradas">
      {reentries.map((item) => {
        const lead = leadByPrediction.get(item.prediction_id);
        const tier = lead ? tierStyle(lead.score) : undefined;
        const active = item.prediction_id === focusedPredictionId;
        return (
          <li key={item.prediction_id}>
            <button
              type="button"
              className="event-row"
              data-tier={tier?.tier ?? "monitor"}
              aria-pressed={active}
              onClick={() => onFocus(item.prediction_id)}
            >
              <span className="event-row__dot" aria-hidden />
              <span className="event-row__id">
                <strong>{item.name}</strong>
                <span>NORAD {item.norad_id} · {formatUtc(item.predicted_reentry_utc)}</span>
              </span>
              <span className="event-row__score">{lead ? scoreToIndex(lead.score) : "--"}</span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
