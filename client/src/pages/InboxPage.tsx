import { useEffect, useState } from "react";
import { api, shortDate } from "@src/lib/api";
import type { InboxMessage } from "@src/types/crm";
import { LoadingState } from "@src/components/LoadingState";

export function InboxPage() {
  const [rows, setRows] = useState<InboxMessage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .inbox()
      .then(setRows)
      .finally(() => setLoading(false));
  }, []);

  async function mark(id: number) {
    const updated = await api.markRead(id);
    setRows((prev) => prev.map((m) => (m.id === id ? updated : m)));
  }

  if (loading) return <LoadingState label="Syncing inbox..." />;

  return (
    <div className="stack">
      {rows.map((m) => (
        <div className="list-row card" key={m.id}>
          <div>
            <strong>
              {m.subject}
              {m.unread ? " · unread" : ""}
            </strong>
            <span>
              {m.from_name} · {shortDate(m.created_at)}
            </span>
            <div style={{ marginTop: 8 }}>{m.preview}</div>
          </div>
          {m.unread ? (
            <button className="btn primary" onClick={() => void mark(m.id)}>
              Mark read
            </button>
          ) : (
            <span className="badge ok">Read</span>
          )}
        </div>
      ))}
    </div>
  );
}
