import { applyQuotaFields, readLocalQuota, type QuotaState, TRY_MAX } from "@src/lib/quota";

export function apiBase(): string {
  return "/api/ai-crm";
}

export class QuotaError extends Error {
  used: number;
  left: number;
  max: number;

  constructor(message: string, quota: QuotaState) {
    super(message);
    this.name = "QuotaError";
    this.used = quota.used;
    this.left = quota.left;
    this.max = quota.max;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  const text = await res.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }
  if (!res.ok) {
    const obj = (data || {}) as {
      error?: string;
      detail?: { error?: string; used?: number; left?: number; max?: number };
      used?: number;
      left?: number;
      max?: number;
    };
    const nested = obj.detail && typeof obj.detail === "object" ? obj.detail : obj;
    const quota = applyQuotaFields(nested);
    const message =
      (typeof nested.error === "string" && nested.error) ||
      (typeof obj.error === "string" && obj.error) ||
      text ||
      `Request failed (${res.status})`;
    if (res.status === 429) throw new QuotaError(message, quota);
    throw new Error(message);
  }
  return data as T;
}

export type AiChatResult = import("@src/types/crm").AiChatResponse & {
  used?: number;
  left?: number;
  max?: number;
  cached?: boolean;
};

export const api = {
  health: () => request<{ ok: boolean }>("/health"),
  usage: async (): Promise<QuotaState> => {
    try {
      const data = await request<{ used?: number; left?: number; max?: number }>("/usage");
      return applyQuotaFields(data);
    } catch {
      return readLocalQuota();
    }
  },
  dashboard: () => request<import("@src/types/crm").Dashboard>("/dashboard"),
  contacts: (q?: string) =>
    request<import("@src/types/crm").Contact[]>(
      `/contacts${q ? `?q=${encodeURIComponent(q)}` : ""}`,
    ),
  companies: (q?: string) =>
    request<import("@src/types/crm").Company[]>(
      `/companies${q ? `?q=${encodeURIComponent(q)}` : ""}`,
    ),
  deals: () => request<import("@src/types/crm").Deal[]>("/deals"),
  updateDealStage: (id: number, stage: string) =>
    request<import("@src/types/crm").Deal>(`/deals/${id}/stage`, {
      method: "PATCH",
      body: JSON.stringify({ stage }),
    }),
  leads: () => request<import("@src/types/crm").Lead[]>("/leads"),
  tasks: () => request<import("@src/types/crm").TaskItem[]>("/tasks"),
  updateTask: (
    id: number,
    body: {
      title: string;
      description: string;
      status: string;
      priority: string;
      due_date: string | null;
      owner: string;
      related_type: string;
      related_id: number | null;
    },
  ) =>
    request<import("@src/types/crm").TaskItem>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  activities: () => request<import("@src/types/crm").Activity[]>("/activities"),
  inbox: () => request<import("@src/types/crm").InboxMessage[]>("/inbox"),
  markRead: (id: number) =>
    request<import("@src/types/crm").InboxMessage>(`/inbox/${id}/read`, {
      method: "POST",
    }),
  aiChat: async (message: string): Promise<AiChatResult> => {
    const data = await request<AiChatResult>("/ai/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    applyQuotaFields(data);
    return data;
  },
  reports: () => request<Record<string, unknown>>("/reports/summary"),
};

export { TRY_MAX };

export function money(n: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

export function shortDate(value: string | null | undefined): string {
  if (!value) return "-";
  return new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}
