import { useEffect, useState } from "react";
import { api, shortDate } from "@src/lib/api";
import type { Contact } from "@src/types/crm";
import { LoadingState } from "@src/components/LoadingState";

export function ContactsPage() {
  const [rows, setRows] = useState<Contact[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      setLoading(true);
      api
        .contacts(q || undefined)
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
          placeholder="Search name, email, title..."
        />
      </div>
      {loading ? (
        <LoadingState label="Loading contacts..." />
      ) : (
        <div className="card table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Name</th>
                <th>Title</th>
                <th>Company</th>
                <th>Owner</th>
                <th>Status</th>
                <th>Last touch</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((c) => (
                <tr key={c.id}>
                  <td>
                    <strong>
                      {c.first_name} {c.last_name}
                    </strong>
                    <div style={{ color: "var(--muted)", fontSize: 12 }}>{c.email}</div>
                  </td>
                  <td>{c.title}</td>
                  <td>{c.company_name ?? "-"}</td>
                  <td>{c.owner}</td>
                  <td>
                    <span className={`badge ${c.status === "active" ? "ok" : "warn"}`}>
                      {c.status}
                    </span>
                  </td>
                  <td>{shortDate(c.last_contacted_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
