import { useEffect, useState } from "react";
import { api, money, shortDate } from "@src/lib/api";
import type { Lead } from "@src/types/crm";
import { LoadingState } from "@src/components/LoadingState";

export function LeadsPage() {
  const [rows, setRows] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .leads()
      .then(setRows)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState label="Scoring leads..." />;

  return (
    <div className="card table-wrap">
      <table className="data">
        <thead>
          <tr>
            <th>Lead</th>
            <th>Company</th>
            <th>Source</th>
            <th>Score</th>
            <th>Status</th>
            <th>Est. value</th>
            <th>Owner</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((l) => (
            <tr key={l.id}>
              <td>
                <strong>{l.name}</strong>
                <div style={{ color: "var(--muted)", fontSize: 12 }}>{l.email}</div>
              </td>
              <td>{l.company_name}</td>
              <td>{l.source}</td>
              <td>
                <span className={`badge ${l.score >= 75 ? "ok" : l.score >= 55 ? "accent" : "warn"}`}>
                  {l.score}
                </span>
              </td>
              <td>{l.status}</td>
              <td>{money(l.estimated_value)}</td>
              <td>{l.owner}</td>
              <td>{shortDate(l.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
