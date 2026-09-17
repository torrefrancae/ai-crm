import { useEffect, useState } from "react";
import { api, money } from "@src/lib/api";
import type { Company } from "@src/types/crm";
import { LoadingState } from "@src/components/LoadingState";

export function CompaniesPage() {
  const [rows, setRows] = useState<Company[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      setLoading(true);
      api
        .companies(q || undefined)
        .then(setRows)
        .finally(() => setLoading(false));
    }, 180);
    return () => window.clearTimeout(handle);
  }, [q]);

  return (
    <div className="stack">
      <div className="search" style={{ maxWidth: 360 }}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search company, industry, city..."
        />
      </div>
      {loading ? (
        <LoadingState />
      ) : (
        <div className="card table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Company</th>
                <th>Industry</th>
                <th>Size</th>
                <th>Location</th>
                <th>Revenue</th>
                <th>Health</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((c) => (
                <tr key={c.id}>
                  <td>
                    <strong>{c.name}</strong>
                    <div style={{ color: "var(--muted)", fontSize: 12 }}>{c.website}</div>
                  </td>
                  <td>{c.industry}</td>
                  <td>{c.size}</td>
                  <td>
                    {c.city}, {c.country}
                  </td>
                  <td>{money(c.annual_revenue)}</td>
                  <td>
                    <span
                      className={`badge ${
                        c.health_score >= 80 ? "ok" : c.health_score >= 65 ? "warn" : "danger"
                      }`}
                    >
                      {c.health_score}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
