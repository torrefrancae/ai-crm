import { useEffect, useState } from "react";
import { api, shortDate } from "@src/lib/api";
import type { Activity } from "@src/types/crm";
import { LoadingState } from "@src/components/LoadingState";

export function ActivitiesPage() {
  const [rows, setRows] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .activities()
      .then(setRows)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState label="Loading activity feed..." />;

  return (
    <div className="stack">
      {rows.map((a) => (
        <div className="list-row card" key={a.id}>
          <div>
            <strong>
              {a.subject}
            </strong>
            <span>
              {a.kind} · {a.contact_name ?? "Internal"} · {a.owner} · {shortDate(a.occurred_at)}
            </span>
            <div style={{ marginTop: 8, color: "var(--text)" }}>{a.body}</div>
          </div>
          <span className="badge accent">{a.kind}</span>
        </div>
      ))}
    </div>
  );
}
