import { CircleAlert, MapPin } from "lucide-react";

import type { RiskRegion } from "../api/types";
import { formatWindow } from "../lib/format";
import { recommendedAction, scopeLabel, scoreToIndex, tierStyle } from "../lib/severity";
import { RiskBadge } from "./RiskBadge";

interface ExposurePanelProps {
  regions: RiskRegion[];
}

/** Quem está sob o corredor: região líder, ativos expostos reais e ação recomendada. */
export function ExposurePanel({ regions }: ExposurePanelProps) {
  const lead = regions[0];
  if (!lead) {
    return (
      <div className="exposure empty-state">
        <p>Sem corredor de risco acima do filtro para este objeto.</p>
      </div>
    );
  }

  const tier = tierStyle(lead.score);
  const assets = [...new Set(regions.flatMap((r) => r.exposed_assets).filter(Boolean))];
  const otherRegions = regions.slice(1, 4);

  return (
    <div className="exposure" data-tier={tier.tier}>
      <div className="exposure__lead">
        <div>
          <span className="exposure__region-label">{scopeLabel(lead.scope)}</span>
          <strong className="exposure__region">{lead.label ?? lead.region}</strong>
        </div>
        <RiskBadge score={lead.score} size="lg" />
      </div>

      <p className="exposure__hint">
        Índice = proximidade ao corredor × exposição. Não é probabilidade de impacto.
      </p>

      <div className="exposure__action" role="note">
        <CircleAlert size={15} strokeWidth={1.75} />
        <span>{recommendedAction(lead.score, lead.scope)}</span>
      </div>

      <div className="exposure__assets">
        <span className="exposure__assets-head">
          Ativos sob o corredor
          <em>{assets.length}</em>
        </span>
        {assets.length ? (
          <ul>
            {assets.slice(0, 6).map((asset) => (
              <li key={asset}>
                <MapPin size={13} strokeWidth={1.75} />
                {asset}
              </li>
            ))}
          </ul>
        ) : (
          <p className="exposure__assets-empty">
            Corredor majoritariamente sobre área despovoada — sem ativos críticos nomeados.
          </p>
        )}
      </div>

      {otherRegions.length ? (
        <div className="exposure__others">
          <span className="exposure__others-head">Outras regiões no corredor</span>
          <ul>
            {otherRegions.map((r) => (
              <li key={`${r.prediction_id}-${r.region}`} data-tier={tierStyle(r.score).tier}>
                <i className="tier-dot" aria-hidden />
                <span>{r.label ?? r.region}</span>
                <b className="exposure__others-num">{scoreToIndex(r.score)}</b>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <span className="exposure__window">Janela {formatWindow(lead.window_utc[0], lead.window_utc[1])}</span>
    </div>
  );
}
