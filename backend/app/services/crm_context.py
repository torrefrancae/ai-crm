from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Activity, Company, Contact, Deal, Lead, Task
from app.schemas import AiChatResponse, DashboardOut


STAGE_LABELS = {
    "qualification": "Qualification",
    "discovery": "Discovery",
    "proposal": "Proposal",
    "negotiation": "Negotiation",
    "closed_won": "Closed Won",
    "closed_lost": "Closed Lost",
}


def build_dashboard(db: Session) -> DashboardOut:
    deals = db.query(Deal).all()
    open_deals = [d for d in deals if d.stage not in ("closed_won", "closed_lost")]
    won = [d for d in deals if d.stage == "closed_won"]
    lost = [d for d in deals if d.stage == "closed_lost"]

    pipeline_value = sum(d.amount for d in open_deals)
    weighted = sum(d.amount * (d.probability / 100.0) for d in open_deals)
    decided = len(won) + len(lost)
    win_rate = (len(won) / decided * 100.0) if decided else 0.0
    avg_deal = (sum(d.amount for d in deals) / len(deals)) if deals else 0.0

    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    won_month = sum(d.amount for d in won if (d.updated_at or d.created_at) >= month_start)

    stage_map: dict[str, float] = defaultdict(float)
    for d in open_deals:
        stage_map[d.stage] += d.amount
    stage_breakdown = [
        {"stage": STAGE_LABELS.get(k, k), "key": k, "value": round(v, 2)}
        for k, v in stage_map.items()
    ]

    revenue_trend = []
    for i in range(5, -1, -1):
        from datetime import timedelta

        anchor = (now.replace(day=1) - timedelta(days=30 * i)).strftime("%b")
        base = avg_deal * (0.7 + (5 - i) * 0.08)
        revenue_trend.append({"month": anchor, "revenue": round(base + (i * 4200), 2)})

    owner_map: dict[str, float] = defaultdict(float)
    for d in open_deals:
        owner_map[d.owner] += d.amount * (d.probability / 100.0)
    top_owners = [
        {"owner": k, "weighted": round(v, 2)}
        for k, v in sorted(owner_map.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    companies = db.query(Company).order_by(Company.health_score.asc()).limit(5).all()
    health_alerts = [
        {
            "company": c.name,
            "health_score": c.health_score,
            "industry": c.industry,
            "city": c.city,
        }
        for c in companies
        if c.health_score < 70
    ]

    tasks_due = (
        db.query(Task)
        .filter(Task.status != "done", Task.due_date != None)  # noqa: E711
        .count()
    )
    new_leads = db.query(Lead).filter(Lead.status.in_(["new", "contacted"])).count()

    return DashboardOut(
        pipeline_value=round(pipeline_value, 2),
        weighted_pipeline=round(weighted, 2),
        open_deals=len(open_deals),
        won_this_month=round(won_month, 2),
        new_leads=new_leads,
        tasks_due=tasks_due,
        avg_deal_size=round(avg_deal, 2),
        win_rate=round(win_rate, 1),
        stage_breakdown=stage_breakdown,
        revenue_trend=revenue_trend,
        top_owners=top_owners,
        health_alerts=health_alerts,
    )


def build_crm_context(db: Session) -> dict:
    dash = build_dashboard(db)
    deals = db.query(Deal).all()
    open_deals = [d for d in deals if d.stage not in ("closed_won", "closed_lost")]
    leads = db.query(Lead).order_by(Lead.score.desc()).limit(8).all()
    tasks = db.query(Task).filter(Task.status != "done").limit(8).all()
    at_risk = db.query(Company).filter(Company.health_score < 65).limit(6).all()
    top = sorted(open_deals, key=lambda d: d.amount * d.probability, reverse=True)[:5]
    activities = db.query(Activity).order_by(Activity.occurred_at.desc()).limit(5).all()

    return {
        "kpis": {
            "pipeline_value": dash.pipeline_value,
            "weighted_pipeline": dash.weighted_pipeline,
            "open_deals": dash.open_deals,
            "win_rate": dash.win_rate,
            "avg_deal_size": dash.avg_deal_size,
            "won_this_month": dash.won_this_month,
            "new_leads": dash.new_leads,
            "tasks_due": dash.tasks_due,
            "contacts": db.query(Contact).count(),
        },
        "top_open_deals": [
            {
                "title": d.title,
                "amount": d.amount,
                "probability": d.probability,
                "stage": d.stage,
                "owner": d.owner,
                "company": d.company.name if d.company else None,
            }
            for d in top
        ],
        "hot_leads": [
            {
                "name": l.name,
                "score": l.score,
                "source": l.source,
                "status": l.status,
                "estimated_value": l.estimated_value,
            }
            for l in leads
            if l.score >= 60
        ],
        "at_risk_accounts": [
            {"name": c.name, "health": c.health_score, "industry": c.industry, "city": c.city}
            for c in at_risk
        ],
        "open_tasks": [
            {
                "title": t.title,
                "priority": t.priority,
                "status": t.status,
                "owner": t.owner,
                "due": t.due_date.isoformat() if t.due_date else None,
            }
            for t in tasks
        ],
        "top_owners": dash.top_owners,
        "recent_activity": [
            {"kind": a.kind, "subject": a.subject, "owner": a.owner} for a in activities
        ],
    }


def heuristic_answer(db: Session, message: str) -> AiChatResponse:
    text = message.lower().strip()
    dash = build_dashboard(db)
    deals = db.query(Deal).all()
    open_deals = [d for d in deals if d.stage not in ("closed_won", "closed_lost")]
    leads = db.query(Lead).order_by(Lead.score.desc()).all()
    tasks = db.query(Task).filter(Task.status != "done").all()
    at_risk = db.query(Company).filter(Company.health_score < 65).all()
    activities = db.query(Activity).order_by(Activity.occurred_at.desc()).limit(8).all()

    insights: list[str] = []
    actions: list[str] = []
    reply_parts: list[str] = []

    if any(k in text for k in ("pipeline", "forecast", "revenue", "deal")):
        top = sorted(open_deals, key=lambda d: d.amount * d.probability, reverse=True)[:3]
        reply_parts.append(
            f"Open pipeline sits at ${dash.pipeline_value:,.0f} "
            f"(${dash.weighted_pipeline:,.0f} weighted) across {dash.open_deals} deals. "
            f"Win rate on decided opportunities is {dash.win_rate}%."
        )
        for d in top:
            insights.append(
                f"{d.title}: ${d.amount:,.0f} at {d.probability}% ({d.stage.replace('_', ' ')})"
            )
        actions.append("Prioritize negotiation-stage deals closing within 14 days")
        actions.append("Re-forecast any deal with no activity in the last 10 days")

    if any(k in text for k in ("lead", "inbound", "score", "prospect")):
        hot = [l for l in leads if l.score >= 75][:4]
        reply_parts.append(
            f"There are {dash.new_leads} fresh or contacted leads in the funnel. "
            f"Highest-intent prospects are scoring above 75."
        )
        for lead in hot:
            insights.append(
                f"{lead.name} ({lead.source}) score {lead.score} - ~${lead.estimated_value:,.0f}"
            )
        actions.append("Convert top-scoring qualified leads into deals this week")
        actions.append("Assign nurture sequences to leads below score 55")

    if any(k in text for k in ("risk", "churn", "health", "retention", "at risk")):
        reply_parts.append(
            f"{len(at_risk)} accounts are below the health threshold of 65. "
            "These accounts need outreach before expansion talks stall."
        )
        for c in at_risk[:4]:
            insights.append(f"{c.name}: health {c.health_score} ({c.industry}, {c.city})")
        actions.append("Schedule health-check calls with low-score accounts")
        actions.append("Offer success plan reviews tied to renewal dates")

    if any(k in text for k in ("task", "todo", "follow", "overdue")):
        overdue = [t for t in tasks if t.due_date and t.due_date < datetime.utcnow()]
        reply_parts.append(
            f"{dash.tasks_due} open tasks are on the board; {len(overdue)} look overdue. "
            "Clearing high-priority blockers usually lifts close rates."
        )
        for t in sorted(tasks, key=lambda x: (x.priority != "high", x.due_date or datetime.max))[:4]:
            insights.append(f"{t.title} [{t.priority}] - {t.status}")
        actions.append("Knock out high-priority overdue tasks before midday")
        actions.append("Batch low-priority follow-ups into a single outreach block")

    if any(k in text for k in ("owner", "rep", "team", "quota", "performance")):
        reply_parts.append("Weighted pipeline by owner shows where coaching time pays off.")
        for row in dash.top_owners:
            insights.append(f"{row['owner']}: ${row['weighted']:,.0f} weighted")
        actions.append("Pair top and bottom performers for deal reviews")
        actions.append("Rebalance lead routing toward owners under capacity")

    if any(k in text for k in ("activity", "call", "email", "meeting", "recent")):
        reply_parts.append("Recent customer-facing activity signals momentum on live deals.")
        for a in activities[:5]:
            insights.append(f"{a.kind}: {a.subject}")
        actions.append("Log next steps on every open negotiation deal")

    if not reply_parts:
        reply_parts.append(
            f"AI-CRM snapshot: ${dash.pipeline_value:,.0f} open pipeline, "
            f"{dash.new_leads} warm leads, win rate {dash.win_rate}%, "
            f"and {len(at_risk)} accounts needing attention."
        )
        insights.extend(
            [
                f"Weighted forecast ${dash.weighted_pipeline:,.0f}",
                f"Average deal size ${dash.avg_deal_size:,.0f}",
                f"Won this month ${dash.won_this_month:,.0f}",
            ]
        )
        actions.extend(
            [
                "Ask about pipeline, leads, risk, tasks, or team performance",
                "Open the Pipeline board and advance stalled cards",
            ]
        )

    return AiChatResponse(
        reply=" ".join(reply_parts),
        insights=insights[:8],
        suggested_actions=actions[:5],
    )
