// Fonte única de severidade. O score do backend é 0–1 (proximidade ao corredor ×
// exposição), NÃO uma probabilidade. Exibimos como índice 0–100 + tier.

export type Tier = "monitor" | "attention" | "elevated" | "critical";

export interface TierStyle {
  tier: Tier;
  label: string;
  /** cor sólida (hex) — para Leaflet/canvas/globo que precisam de cor crua */
  color: string;
  /** preenchimento translúcido — fills de corredor/badge */
  soft: string;
}

const ORDER: Record<Tier, number> = {
  monitor: 0,
  attention: 1,
  elevated: 2,
  critical: 3,
};

const STYLES: Record<Tier, TierStyle> = {
  monitor: { tier: "monitor", label: "Monitorar", color: "#3DD6C4", soft: "rgba(61,214,196,0.14)" },
  attention: { tier: "attention", label: "Atenção", color: "#F0A202", soft: "rgba(240,162,2,0.16)" },
  elevated: { tier: "elevated", label: "Elevado", color: "#FF8A2A", soft: "rgba(255,138,42,0.16)" },
  critical: { tier: "critical", label: "Crítico", color: "#FF4D2E", soft: "rgba(255,77,46,0.18)" },
};

export function tierOf(score: number): Tier {
  if (score >= 0.7) return "critical";
  if (score >= 0.45) return "elevated";
  if (score >= 0.2) return "attention";
  return "monitor";
}

export function tierStyle(score: number): TierStyle {
  return STYLES[tierOf(score)];
}

export function tierRank(tier: Tier): number {
  return ORDER[tier];
}

/** 0–1 → índice inteiro 0–100. */
export function scoreToIndex(score: number): number {
  return Math.round(score * 100);
}

export type Scope = "ocean" | "land" | "br_state" | string | null | undefined;

export function scopeLabel(scope: Scope): string {
  switch (scope) {
    case "ocean":
      return "Corredor oceânico";
    case "br_state":
      return "Estado brasileiro";
    case "land":
      return "Região continental";
    default:
      return "Região monitorada";
  }
}

/** Ação operacional recomendada — derivada do tier e do tipo de região. */
export function recommendedAction(score: number, scope: Scope): string {
  const tier = tierOf(score);
  if (tier === "critical") {
    return scope === "ocean"
      ? "Alertar autoridades de aviação e tráfego marítimo na rota; emitir aviso (NOTAM)."
      : "Acionar Defesa Civil e DECEA; emitir aviso à aviação (NOTAM) na janela.";
  }
  if (tier === "elevated") {
    return "Notificar autoridades regionais e preparar aviso à aviação caso o corredor se confirme.";
  }
  if (tier === "attention") {
    return "Acompanhar a janela de incerteza; reavaliar a cada atualização de previsão.";
  }
  return "Acompanhamento de rotina — sem ação imediata.";
}
