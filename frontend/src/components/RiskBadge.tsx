import { scoreToIndex, tierStyle } from "../lib/severity";

interface RiskBadgeProps {
  score: number;
  size?: "sm" | "md" | "lg";
  showTier?: boolean;
}

/** Índice de risco 0–100 + tier. NÃO é porcentagem (proximidade × exposição). */
export function RiskBadge({ score, size = "md", showTier = true }: RiskBadgeProps) {
  const t = tierStyle(score);
  return (
    <span className={`risk-badge risk-badge--${size}`} data-tier={t.tier}>
      <span className="risk-badge__num">
        <span className="risk-badge__index">{scoreToIndex(score)}</span>
        <span className="risk-badge__scale">/100</span>
      </span>
      {showTier ? <span className="risk-badge__tier">{t.label}</span> : null}
    </span>
  );
}
