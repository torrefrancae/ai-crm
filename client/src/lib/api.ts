const API_BASE = "/sample/ai-crm/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ ok: boolean }>("/health"),
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
  updateTask: (id: number, body: {
      title: string;
      description: string;
      status: string;
      priority: string;
      due_date: string | null;
      owner: string;
      related_type: string;
      related_id: number | null;
    }) =>
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
  aiChat: (message: string) =>
    request<import("@src/types/crm").AiChatResponse>("/ai/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
  reports: () => request<Record<string, unknown>>("/reports/summary"),
};

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
