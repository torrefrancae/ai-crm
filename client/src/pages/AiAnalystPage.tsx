import { useState } from "react";
import type { FormEvent } from "react";
import { api } from "@src/lib/api";
import type { AiChatResponse } from "@src/types/crm";

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

export function AiAnalystPage() {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [log, setLog] = useState<ChatItem[]>([
    {
      role: "assistant",
      text: "I read live CRM metrics from this workspace. Ask about pipeline, leads, account risk, tasks, or team performance.",
    },
  ]);

  async function ask(message: string) {
    const trimmed = message.trim();
    if (!trimmed || busy) return;
    setBusy(true);
    setLog((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");
    try {
      const res: AiChatResponse = await api.aiChat(trimmed);
      setLog((prev) => [
        ...prev,
        {
          role: "assistant",
          text: res.reply,
          insights: res.insights,
          actions: res.suggested_actions,
        },
      ]);
    } catch (err) {
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

  return (
    <div className="ai-layout">
      <div className="card">
        <div className="panel-title">
          <h3>Conversation</h3>
          {busy ? <span className="badge accent">Thinking...</span> : null}
        </div>
        <div className="chips">
          {prompts.map((p) => (
            <button key={p} className="chip" type="button" onClick={() => void ask(p)}>
              {p}
            </button>
          ))}
        </div>
        <div className="chat-log">
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
        </div>
        <form className="chat-form" onSubmit={onSubmit}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the analytics assistant..."
          />
          <button className="btn primary" type="submit" disabled={busy}>
            Ask
          </button>
        </form>
      </div>
      <div className="card stack">
        <div className="panel-title">
          <h3>What this AI covers</h3>
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
        <div className="list-row">
          <div>
            <strong>Execution hygiene</strong>
            <span>Overdue tasks and recent activity signals</span>
          </div>
        </div>
      </div>
    </div>
  );
}
