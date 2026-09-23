export const TRY_MAX = 5;
export const UNLIMITED_MAX = 9999;

const LOCAL_USED = "ai_crm_tries_used";
const LOCAL_LIMITS = "ai_crm_limits_enabled";

export type QuotaState = {
  used: number;
  left: number;
  max: number;
  limitsEnabled: boolean;
};

function readLimitsFlag(): boolean {
  try {
    const raw = window.localStorage.getItem(LOCAL_LIMITS);
    if (raw === "0") return false;
    if (raw === "1") return true;
  } catch {
    /* private mode */
  }
  return true;
}

function writeLimitsFlag(enabled: boolean): void {
  try {
    window.localStorage.setItem(LOCAL_LIMITS, enabled ? "1" : "0");
  } catch {
    /* private mode */
  }
}

export function readLocalQuota(): QuotaState {
  const limitsEnabled = readLimitsFlag();
  if (!limitsEnabled) {
    return { used: 0, left: UNLIMITED_MAX, max: UNLIMITED_MAX, limitsEnabled: false };
  }
  try {
    const n = Number(window.localStorage.getItem(LOCAL_USED));
    const used = Number.isFinite(n) ? Math.max(0, Math.min(TRY_MAX, Math.floor(n))) : 0;
    return { used, left: Math.max(0, TRY_MAX - used), max: TRY_MAX, limitsEnabled: true };
  } catch {
    return { used: 0, left: TRY_MAX, max: TRY_MAX, limitsEnabled: true };
  }
}

export function writeLocalQuota(used: number, max = TRY_MAX, limitsEnabled = true): QuotaState {
  if (!limitsEnabled) {
    writeLimitsFlag(false);
    return { used: 0, left: UNLIMITED_MAX, max: UNLIMITED_MAX, limitsEnabled: false };
  }
  writeLimitsFlag(true);
  const nextUsed = Math.max(0, Math.min(max, Math.floor(used)));
  try {
    window.localStorage.setItem(LOCAL_USED, String(nextUsed));
  } catch {
    /* private mode */
  }
  return { used: nextUsed, left: Math.max(0, max - nextUsed), max, limitsEnabled: true };
}

export function applyQuotaFields(data: {
  used?: number;
  left?: number;
  max?: number;
  limitsEnabled?: boolean;
}): QuotaState {
  if (data.limitsEnabled === false) {
    return writeLocalQuota(0, UNLIMITED_MAX, false);
  }
  const max = typeof data.max === "number" ? data.max : TRY_MAX;
  if (typeof data.used === "number") return writeLocalQuota(data.used, max, true);
  if (typeof data.left === "number") return writeLocalQuota(max - data.left, max, true);
  return readLocalQuota();
}
