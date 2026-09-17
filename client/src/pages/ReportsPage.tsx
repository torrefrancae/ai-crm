import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, money } from "@src/lib/api";
import { LoadingState } from "@src/components/LoadingState";
import { useChartTheme } from "@src/hooks/useChartTheme";

type ReportPayload = {
  kpis: {
    pipeline_value: number;
    weighted_pipeline: number;
    win_rate: number;
    avg_deal_size: number;
    won_this_month: number;
    new_leads: number;
  };
  stage_breakdown: { stage: string; value: number }[];
  revenue_trend: { month: string; revenue: number }[];
  top_owners: { owner: string; weighted: number }[];
  health_alerts: { company: string; health_score: number }[];
};

export function ReportsPage() {
  const [data, setData] = useState<ReportPayload | null>(null);
  const chart = useChartTheme();

  useEffect(() => {
    api.reports().then((raw) => setData(raw as ReportPayload));
  }, []);

  if (!data) return <LoadingState label="Building reports..." />;

  return (
    <div className="stack">
      <div className="grid-kpi">
        <div className="card kpi">
          <div className="label">Pipeline</div>
          <div className="value">{money(data.kpis.pipeline_value)}</div>
        </div>
        <div className="card kpi">
          <div className="label">Weighted</div>
          <div className="value">{money(data.kpis.weighted_pipeline)}</div>
        </div>
        <div className="card kpi">
          <div className="label">Won month</div>
          <div className="value">{money(data.kpis.won_this_month)}</div>
        </div>
        <div className="card kpi">
          <div className="label">Win rate</div>
          <div className="value">{data.kpis.win_rate}%</div>
        </div>
      </div>

      <div className="panel-grid">
        <div className="card">
          <div className="panel-title">
            <h3>Owner contribution</h3>
          </div>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={data.top_owners}>
                <CartesianGrid stroke={chart.grid} vertical={false} />
                <XAxis dataKey="owner" stroke={chart.muted} fontSize={11} />
                <YAxis stroke={chart.muted} fontSize={12} tickFormatter={(v) => `$${v / 1000}k`} />
                <Tooltip contentStyle={chart.tooltip} />
                <Bar dataKey="weighted" fill={chart.accent} radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card">
          <div className="panel-title">
            <h3>Revenue cadence</h3>
          </div>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <LineChart data={data.revenue_trend}>
                <CartesianGrid stroke={chart.grid} vertical={false} />
                <XAxis dataKey="month" stroke={chart.muted} fontSize={12} />
                <YAxis stroke={chart.muted} fontSize={12} tickFormatter={(v) => `$${v / 1000}k`} />
                <Tooltip contentStyle={chart.tooltip} />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke={chart.accent2}
                  strokeWidth={3}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card table-wrap">
        <div className="panel-title">
          <h3>Health watchlist</h3>
        </div>
        <table className="data">
          <thead>
            <tr>
              <th>Company</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {data.health_alerts.map((row) => (
              <tr key={row.company}>
                <td>{row.company}</td>
                <td>
                  <span className="badge danger">{row.health_score}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
