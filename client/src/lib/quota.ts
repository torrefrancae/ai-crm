export const TRY_MAX = 5;

const LOCAL_USED = "ai_crm_tries_used";

export type QuotaState = {
  used: number;
  left: number;
  max: number;
};

export function readLocalQuota(): QuotaState {
  try {
    const n = Number(window.localStorage.getItem(LOCAL_USED));
    const used = Number.isFinite(n) ? Math.max(0, Math.min(TRY_MAX, Math.floor(n))) : 0;
    return { used, left: Math.max(0, TRY_MAX - used), max: TRY_MAX };
  } catch {
    return { used: 0, left: TRY_MAX, max: TRY_MAX };
  }
}

export function writeLocalQuota(used: number, max = TRY_MAX): QuotaState {
  const nextUsed = Math.max(0, Math.min(max, Math.floor(used)));
  try {
    window.localStorage.setItem(LOCAL_USED, String(nextUsed));
  } catch {
    /* private mode */
  }
  return { used: nextUsed, left: Math.max(0, max - nextUsed), max };
}

export function applyQuotaFields(data: { used?: number; left?: number; max?: number }): QuotaState {
  const max = typeof data.max === "number" ? data.max : TRY_MAX;
  if (typeof data.used === "number") return writeLocalQuota(data.used, max);
  if (typeof data.left === "number") return writeLocalQuota(max - data.left, max);
  return readLocalQuota();
}
