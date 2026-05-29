import type { Confidence, ObjectType } from "../api/types";

export const OBJECT_TYPE_LABEL: Record<ObjectType, string> = {
  payload: "Satélite",
  rocket_body: "Estágio de foguete",
  debris: "Detrito",
};

export const CONFIDENCE_LABEL: Record<Confidence, string> = {
  low: "Confiança baixa",
  medium: "Confiança média",
  high: "Confiança alta",
};
