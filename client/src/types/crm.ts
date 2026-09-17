export type Company = {
  id: number;
  name: string;
  industry: string;
  size: string;
  website: string;
  city: string;
  country: string;
  annual_revenue: number;
  health_score: number;
  created_at: string;
};

export type Contact = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  title: string;
  status: string;
  owner: string;
  company_id: number | null;
  last_contacted_at: string | null;
  created_at: string;
  company_name?: string | null;
};

export type Lead = {
  id: number;
  name: string;
  email: string;
  company_name: string;
  source: string;
  status: string;
  score: number;
  owner: string;
  estimated_value: number;
  notes: string;
  created_at: string;
};

export type Deal = {
  id: number;
  title: string;
  stage: string;
  amount: number;
  probability: number;
  close_date: string | null;
  owner: string;
  company_id: number | null;
  contact_id: number | null;
  created_at: string;
  updated_at: string;
  company_name?: string | null;
  contact_name?: string | null;
};

export type TaskItem = {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  due_date: string | null;
  owner: string;
  related_type: string;
  related_id: number | null;
  created_at: string;
};

export type Activity = {
  id: number;
  kind: string;
  subject: string;
  body: string;
  contact_id: number | null;
  deal_id: number | null;
  owner: string;
  occurred_at: string;
  contact_name?: string | null;
};

export type InboxMessage = {
  id: number;
  thread: string;
  direction: string;
  from_name: string;
  subject: string;
  preview: string;
  unread: number;
  created_at: string;
};

export type Dashboard = {
  pipeline_value: number;
  weighted_pipeline: number;
  open_deals: number;
  won_this_month: number;
  new_leads: number;
  tasks_due: number;
  avg_deal_size: number;
  win_rate: number;
  stage_breakdown: { stage: string; key: string; value: number }[];
  revenue_trend: { month: string; revenue: number }[];
  top_owners: { owner: string; weighted: number }[];
  health_alerts: {
    company: string;
    health_score: number;
    industry: string;
    city: string;
  }[];
};

export type AiChatResponse = {
  reply: string;
  insights: string[];
  suggested_actions: string[];
};

export const DEAL_STAGES = [
  { key: "qualification", label: "Qualification" },
  { key: "discovery", label: "Discovery" },
  { key: "proposal", label: "Proposal" },
  { key: "negotiation", label: "Negotiation" },
  { key: "closed_won", label: "Closed Won" },
  { key: "closed_lost", label: "Closed Lost" },
] as const;
