function trimSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

function withTrailingSlash(value: string): string {
  const trimmed = value.trim() || "/";
  return trimmed.endsWith("/") ? trimmed : `${trimmed}/`;
}

export function sampleBase(): string {
  return withTrailingSlash(import.meta.env.VITE_BASE || "/sample/ai-crm/");
}

export function sampleBasename(): string {
  return trimSlash(sampleBase()) || "/";
}

export function apiBase(): string {
  return trimSlash(import.meta.env.VITE_API_BASE || "/api/ai-crm") || "/api/ai-crm";
}
