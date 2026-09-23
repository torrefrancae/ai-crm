import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { api, QuotaError, TRY_MAX } from "@src/lib/api";
import { applyQuotaFields, readLocalQuota, type QuotaState } from "@src/lib/quota";
import {
  describeWait,
  estimateWaitMs,
  formatSeconds,
  recordWaitMs,
} from "@src/lib/waitEstimate";

type ChatItem = {
  role: "user" | "assistant";
  text: string;
  insights?: string[];
  actions?: string[];
};

const prompts = [
  "How healthy is our pipeline right now?",
  "Which leads should we convert this week?",
  "Show me at-risk accounts",
  "What tasks are overdue?",
  "Who is carrying the most weighted pipeline?",
];

function publicInsights(insights: string[] | undefined): string[] | undefined {
  if (!insights?.length) return undefined;
  return insights
    .map((item) =>
      item
        .replace(/\bCursor\s+[A-Za-z0-9._-]+/gi, "Live analyst")
        .replace(/\bcomposer-[A-Za-z0-9._-]+/gi, "auto")
        .replace(/\bgpt-[A-Za-z0-9._-]+/gi, "auto")
        .replace(/\bclaude-[A-Za-z0-9._-]+/gi, "auto")
        .replace(/\bgemini-[A-Za-z0-9._-]+/gi, "auto"),
    )
    .filter(Boolean);
}

export function AiAnalystPage() {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [estimateMs, setEstimateMs] = useState(() => estimateWaitMs());
  const [quota, setQuota] = useState<QuotaState>(() => readLocalQuota());
  const [log, setLog] = useState<ChatItem[]>(() => {
    const start = readLocalQuota();
    return [
      {
        role: "assistant",
        text: start.limitsEnabled
          ? `I analyze a live CRM snapshot through a secure auto-routed assistant. Up to ${TRY_MAX} live prompts per visitor; cached repeats stay free.`
          : "I analyze a live CRM snapshot through a secure auto-routed assistant. Local limits are off, so live prompts are unlimited.",
      },
    ];
  });
  const logRef = useRef<HTMLDivElement | null>(null);
  const startedRef = useRef(0);
  const spent = quota.limitsEnabled && quota.left <= 0;
  const unlimited = !quota.limitsEnabled;

  useEffect(() => {
    void api.usage().then(setQuota).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!busy) {
      setElapsedMs(0);
      return;
    }
    startedRef.current = Date.now();
    const tick = window.setInterval(() => {
      setElapsedMs(Date.now() - startedRef.current);
    }, 200);
    return () => window.clearInterval(tick);
  }, [busy]);

  useEffect(() => {
    const node = logRef.current;
    if (!node) return;
    node.scrollTop = node.scrollHeight;
  }, [log, busy, elapsedMs]);

  async function ask(message: string) {
    const trimmed = message.trim();
    if (!trimmed || busy) return;
    const nextEstimate = estimateWaitMs();
    setEstimateMs(nextEstimate);
    setBusy(true);
    setLog((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");
    const t0 = Date.now();
    try {
      const res = await api.aiChat(trimmed);
      const took = Date.now() - t0;
      if (took >= 800 && !res.cached) recordWaitMs(took);
      setQuota(applyQuotaFields(res));
      const suffix =
        unlimited || typeof res.left !== "number"
          ? res.cached
            ? " (cache hit)"
            : ""
          : ` (${res.left} of ${res.max ?? TRY_MAX} live prompts left${res.cached ? ", cache hit" : ""})`;
      setLog((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `${res.reply}${suffix}`,
          insights: publicInsights(res.insights),
          actions: res.suggested_actions,
        },
      ]);
    } catch (err) {
      if (err instanceof QuotaError) {
        setQuota({
          used: err.used,
          left: err.left,
          max: err.max,
          limitsEnabled: err.limitsEnabled,
        });
      }
      setLog((prev) => [
        ...prev,
        {
          role: "assistant",
          text: err instanceof Error ? err.message : "AI request failed",
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void ask(input);
  }

  const wait = describeWait(estimateMs, elapsedMs);

  return (
    <div className="ai-layout">
      <div className="card">
        <div className="panel-title">
          <h3>Conversation</h3>
          {busy ? (
            <span className="badge accent ai-status">
              <span className="spinner" aria-hidden />
              Usually ~{formatSeconds(estimateMs)}
            </span>
          ) : (
            <span className="badge accent">
              {unlimited
                ? "Unlimited (local)"
                : spent
                  ? `All ${quota.max} live prompts used`
                  : `${quota.left} of ${quota.max} live prompts left`}
            </span>
          )}
        </div>
        {unlimited ? null : (
          <div className="quota-pips" aria-hidden>
            {Array.from({ length: Math.min(quota.max, 24) }, (_, i) => (
              <span key={i} className={i < quota.left ? "pip on" : "pip off"} />
            ))}
          </div>
        )}
        {spent ? (
          <div className="list-row" style={{ marginBottom: 12 }}>
            <div>
              <strong>Prompt limit reached</strong>
              <span>Live AI asks are paused for this visitor. Cached repeats still work if available.</span>
            </div>
          </div>
        ) : null}
        <div className="chips">
          {prompts.map((p) => (
            <button
              key={p}
              className="chip"
              type="button"
              disabled={busy}
              onClick={() => void ask(p)}
            >
              {p}
            </button>
          ))}
        </div>
        <div className="chat-log" ref={logRef} aria-live="polite">
          {log.map((item, idx) => (
            <div key={`${item.role}-${idx}`} className={`bubble ${item.role}`}>
              <div>{item.text}</div>
              {item.insights && item.insights.length > 0 ? (
                <ul style={{ margin: "10px 0 0", paddingLeft: 18 }}>
                  {item.insights.map((insight) => (
                    <li key={insight}>{insight}</li>
                  ))}
                </ul>
              ) : null}
              {item.actions && item.actions.length > 0 ? (
                <div style={{ marginTop: 10 }}>
                  {item.actions.map((action) => (
                    <div key={action} className="badge accent" style={{ margin: "0 6px 6px 0" }}>
                      {action}
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          ))}
          {busy ? (
            <div className="bubble assistant ai-pending" role="status">
              <div className="ai-pending-row">
                <span className="spinner lg" aria-hidden />
                <div>
                  <strong>{wait.headline}</strong>
                  <div className="ai-pending-copy">{wait.detail}</div>
                </div>
              </div>
              <div
                className="ai-progress-track"
                aria-hidden="true"
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={wait.pct}
              >
                <div className="ai-progress-fill" style={{ width: `${wait.pct}%` }} />
              </div>
            </div>
          ) : null}
        </div>
        <form className="chat-form" onSubmit={onSubmit}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              spent ? "Live limit reached - cached repeats may still work..." : busy ? "Waiting on analyst..." : "Ask the analytics assistant..."
            }
            disabled={busy}
            maxLength={600}
          />
          <button
            className="btn primary"
            type="submit"
            disabled={busy || !input.trim()}
          >
            {busy ? "Working..." : "Ask"}
          </button>
        </form>
      </div>
      <div className="card stack">
        <div className="panel-title">
          <h3>Live analyst</h3>
        </div>
        <div className="list-row">
          <div>
            <strong>Secure quota</strong>
            <span>
              {unlimited
                ? "Prompt limits disabled on this PC only (AI_CRM_LOCAL_DEV=1 + AI_CRM_LIMITS_ENABLED=0). Production keeps limits on."
                : "Server-side IP limits, one inflight ask, short cooldown, daily budget"}
            </span>
          </div>
        </div>
        <div className="list-row">
          <div>
            <strong>Speed path</strong>
            <span>Cached CRM snapshot + answer reuse + auto-routed assistant</span>
          </div>
        </div>
        <div className="list-row">
          <div>
            <strong>Forecast and stage mix</strong>
            <span>Weighted pipeline, win rate, and deal concentration</span>
          </div>
        </div>
        <div className="list-row">
          <div>
            <strong>Lead intent</strong>
            <span>Score-ranked prospects and conversion nudges</span>
          </div>
        </div>
        <div className="list-row">
          <div>
            <strong>Account risk</strong>
            <span>Health scores under 65 with outreach prompts</span>
          </div>
        </div>
      </div>
    </div>
  );
}
