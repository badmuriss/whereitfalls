import { Globe, Map as MapIcon } from "lucide-react";

export type StageView = "globe" | "map";

interface StageToggleProps {
  value: StageView;
  onChange: (view: StageView) => void;
}

/** Alterna o palco central entre globo 3D e mapa 2D do corredor (mesmo evento). */
export function StageToggle({ value, onChange }: StageToggleProps) {
  return (
    <div className="stage-toggle" role="group" aria-label="Visualização">
      <button
        type="button"
        className="stage-toggle__btn"
        aria-pressed={value === "globe"}
        onClick={() => onChange("globe")}
      >
        <Globe size={15} strokeWidth={1.75} />
        Globo
      </button>
      <button
        type="button"
        className="stage-toggle__btn"
        aria-pressed={value === "map"}
        onClick={() => onChange("map")}
      >
        <MapIcon size={15} strokeWidth={1.75} />
        Mapa
      </button>
    </div>
  );
}
