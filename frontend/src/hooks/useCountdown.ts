import { formatCountdown } from "../lib/format";
import { useNow } from "./useNow";

/** Contagem regressiva viva até `targetIso`. Texto troca a cada segundo (sem animar). */
export function useCountdown(targetIso: string | undefined): { label: string; past: boolean } {
  const now = useNow(1000);
  if (!targetIso) return { label: "T- --:--:--", past: false };
  return formatCountdown(targetIso, now);
}
