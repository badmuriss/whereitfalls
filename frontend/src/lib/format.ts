const UTC_FMT = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "UTC",
  timeZoneName: "short",
});

const CLOCK_FMT = new Intl.DateTimeFormat("pt-BR", {
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  timeZone: "UTC",
});

export function formatUtc(value: string): string {
  return UTC_FMT.format(new Date(value));
}

export function formatClockUtc(date: Date): string {
  return `${CLOCK_FMT.format(date)} UTC`;
}

export function formatWindow(start: string, end: string): string {
  return `${formatUtc(start)} → ${formatUtc(end)}`;
}

const pad = (n: number) => String(n).padStart(2, "0");

/**
 * Conta o tempo até `targetIso`. Retorna o rótulo "T- HH:MM:SS" (ou com dias se
 * faltar muito) e um flag se a janela já passou ("T+").
 */
export function formatCountdown(targetIso: string, now: number = Date.now()): {
  label: string;
  past: boolean;
} {
  const diffMs = new Date(targetIso).getTime() - now;
  const past = diffMs < 0;
  const total = Math.floor(Math.abs(diffMs) / 1000);
  const days = Math.floor(total / 86400);
  const hours = Math.floor((total % 86400) / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const seconds = total % 60;
  const sign = past ? "T+" : "T-";
  const body = days > 0
    ? `${days}d ${pad(hours)}:${pad(minutes)}:${pad(seconds)}`
    : `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  return { label: `${sign} ${body}`, past };
}
