const STORAGE_KEY = "ai-crm-wait-ms";
export const DEFAULT_MS = 5000;
const MAX_SAMPLES = 8;
const MIN_MS = 800;
const MAX_MS = 45000;

function clamp(ms: number) {
  return Math.max(MIN_MS, Math.min(MAX_MS, Math.round(ms)));
}

function readSamples(): number[] {
  try {
    const raw = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "[]") as unknown;
    if (!Array.isArray(raw)) return [];
    return raw
      .map((n) => Number(n))
      .filter((n) => Number.isFinite(n) && n >= MIN_MS && n <= MAX_MS)
      .slice(-MAX_SAMPLES);
  } catch {
    return [];
  }
}

export function estimateWaitMs(): number {
  const samples = readSamples();
  if (!samples.length) return DEFAULT_MS;
  const sum = samples.reduce((a, b) => a + b, 0);
  return clamp(sum / samples.length);
}

export function recordWaitMs(ms: number): void {
  try {
    const next = [...readSamples(), clamp(ms)].slice(-MAX_SAMPLES);
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    /* private mode */
  }
}

export function sampleCount(): number {
  return readSamples().length;
}

export function formatSeconds(ms: number): string {
  const sec = Math.max(1, Math.round(ms / 1000));
  return `${sec}s`;
}

export function formatClock(ms: number): string {
  const total = Math.max(0, Math.round(ms / 1000));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function etaBand(estimateMs: number): { lowMs: number; highMs: number } {
  const mid = clamp(estimateMs);
  const spread = Math.max(1200, Math.round(mid * 0.25));
  return {
    lowMs: clamp(mid - spread),
    highMs: clamp(mid + spread),
  };
}

export type WaitCopy = {
  headline: string;
  detail: string;
  remainMs: number;
  pct: number;
};

export function describeWait(estimateMs: number, elapsedMs: number): WaitCopy {
  const estimate = clamp(estimateMs);
  const elapsed = Math.max(0, Math.round(elapsedMs));
  const remainMs = Math.max(0, estimate - elapsed);
  const pct = Math.min(98, Math.round((elapsed / Math.max(estimate, 1)) * 100));
  const { lowMs, highMs } = etaBand(estimate);
  const samples = sampleCount();
  const band = `${formatSeconds(lowMs)}-${formatSeconds(highMs)}`;
  const source =
    samples > 0
      ? `based on how long the last ${samples} ${samples === 1 ? "answer" : "answers"} took`
      : "typical wait for a first visit";

  if (remainMs <= 800) {
    return {
      headline: "Almost there - reply should appear any moment",
      detail: `Most replies take ${band} · ${formatClock(elapsed)} so far (${source})`,
      remainMs,
      pct: Math.max(pct, 90),
    };
  }

  return {
    headline: `Please wait - usually about ${formatSeconds(estimate)}`,
    detail: `Most replies take ${band} · ${formatClock(elapsed)} so far · about ${formatSeconds(remainMs)} left (${source})`,
    remainMs,
    pct,
  };
}
