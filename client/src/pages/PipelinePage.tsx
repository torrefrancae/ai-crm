import { useEffect, useMemo, useState } from "react";
import { api, money, shortDate } from "@src/lib/api";
import type { Deal } from "@src/types/crm";
import { DEAL_STAGES } from "@src/types/crm";
import { LoadingState } from "@src/components/LoadingState";

export function PipelinePage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [dragging, setDragging] = useState<number | null>(null);

  const load = () =>
    api
      .deals()
      .then(setDeals)
      .finally(() => setLoading(false));

  useEffect(() => {
    void load();
  }, []);

  const byStage = useMemo(() => {
    const map: Record<string, Deal[]> = {};
    for (const stage of DEAL_STAGES) map[stage.key] = [];
    for (const deal of deals) {
      if (!map[deal.stage]) map[deal.stage] = [];
      map[deal.stage].push(deal);
    }
    return map;
  }, [deals]);

  async function moveDeal(dealId: number, stage: string) {
    const updated = await api.updateDealStage(dealId, stage);
    setDeals((prev) => prev.map((d) => (d.id === dealId ? updated : d)));
  }

  if (loading) return <LoadingState label="Loading pipeline board..." />;

  return (
    <div className="pipeline">
      {DEAL_STAGES.map((stage) => {
        const lane = byStage[stage.key] ?? [];
        const total = lane.reduce((sum, d) => sum + d.amount, 0);
        return (
          <div
            className="lane"
            key={stage.key}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => {
              if (dragging != null) void moveDeal(dragging, stage.key);
              setDragging(null);
            }}
          >
            <h4>
              <span>{stage.label}</span>
              <span>
                {lane.length} · {money(total)}
              </span>
            </h4>
            {lane.map((deal) => (
              <article
                className="deal-card"
                key={deal.id}
                draggable
                onDragStart={() => setDragging(deal.id)}
              >
                <h5>{deal.title}</h5>
                <div className="deal-meta">
                  <span>{money(deal.amount)} · {deal.probability}%</span>
                  <span>{deal.company_name ?? "No company"}</span>
                  <span>
                    {deal.owner} · close {shortDate(deal.close_date)}
                  </span>
                </div>
                <div style={{ marginTop: 10, display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {DEAL_STAGES.filter((s) => s.key !== deal.stage)
                    .slice(0, 2)
                    .map((s) => (
                      <button
                        key={s.key}
                        className="btn ghost"
                        style={{ padding: "4px 8px", fontSize: 12 }}
                        onClick={() => void moveDeal(deal.id, s.key)}
                      >
                        → {s.label}
                      </button>
                    ))}
                </div>
              </article>
            ))}
          </div>
        );
      })}
    </div>
  );
}
