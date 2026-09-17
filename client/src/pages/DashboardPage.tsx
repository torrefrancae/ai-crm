import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, money } from "@src/lib/api";
import type { Dashboard } from "@src/types/crm";
import { LoadingState } from "@src/components/LoadingState";

export function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .dashboard()
      .then(setData)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) return <div className="card">Could not load dashboard: {error}</div>;
  if (!data) return <LoadingState label="Pulling pipeline metrics..." />;

  return (
    <div className="stack">
      <div className="grid-kpi">
        <div className="card kpi">
          <div className="label">Open pipeline</div>
          <div className="value">{money(data.pipeline_value)}</div>
          <div className="hint">{data.open_deals} active deals</div>
        </div>
        <div className="card kpi">
          <div className="label">Weighted forecast</div>
          <div className="value">{money(data.weighted_pipeline)}</div>
          <div className="hint">Probability-adjusted</div>
        </div>
        <div className="card kpi">
          <div className="label">Win rate</div>
          <div className="value">{data.win_rate}%</div>
          <div className="hint">Avg deal {money(data.avg_deal_size)}</div>
        </div>
        <div className="card kpi">
          <div className="label">Today focus</div>
          <div className="value">{data.tasks_due}</div>
          <div className="hint">{data.new_leads} warm leads waiting</div>
        </div>
      </div>

      <div className="panel-grid">
        <div className="card">
          <div className="panel-title">
            <h3>Revenue trend</h3>
            <span className="badge accent">Last 6 months</span>
          </div>
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <AreaChart data={data.revenue_trend}>
                <defs>
                  <linearGradient id="rev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2bb7a0" stopOpacity={0.55} />
                    <stop offset="100%" stopColor="#2bb7a0" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(214,226,236,0.08)" vertical={false} />
                <XAxis dataKey="month" stroke="#93a4b3" fontSize={12} />
                <YAxis stroke="#93a4b3" fontSize={12} tickFormatter={(v) => `$${v / 1000}k`} />
                <Tooltip
                  contentStyle={{
                    background: "#18232e",
                    border: "1px solid rgba(214,226,236,0.12)",
                    borderRadius: 12,
                  }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#2bb7a0" fill="url(#rev)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="panel-title">
            <h3>Stage mix</h3>
          </div>
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={data.stage_breakdown}>
                <CartesianGrid stroke="rgba(214,226,236,0.08)" vertical={false} />
                <XAxis dataKey="stage" stroke="#93a4b3" fontSize={11} />
                <YAxis stroke="#93a4b3" fontSize={12} tickFormatter={(v) => `$${v / 1000}k`} />
                <Tooltip
                  contentStyle={{
                    background: "#18232e",
                    border: "1px solid rgba(214,226,236,0.12)",
                    borderRadius: 12,
                  }}
                />
                <Bar dataKey="value" fill="#f0b429" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="panel-grid">
        <div className="card">
          <div className="panel-title">
            <h3>Top owners</h3>
          </div>
          <div className="stack">
            {data.top_owners.map((row) => (
              <div className="list-row" key={row.owner}>
                <div>
                  <strong>{row.owner}</strong>
                  <span>Weighted pipeline contribution</span>
                </div>
                <strong>{money(row.weighted)}</strong>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="panel-title">
            <h3>Account health alerts</h3>
          </div>
          <div className="stack">
            {data.health_alerts.length === 0 && (
              <div className="list-row">
                <div>
                  <strong>All clear</strong>
                  <span>No accounts under the health threshold</span>
                </div>
              </div>
            )}
            {data.health_alerts.map((row) => (
              <div className="list-row" key={row.company}>
                <div>
                  <strong>{row.company}</strong>
                  <span>
                    {row.industry} · {row.city}
                  </span>
                </div>
                <span className="badge danger">Health {row.health_score}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
