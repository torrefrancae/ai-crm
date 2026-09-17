from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AiChatRequest, AiChatResponse, DashboardOut
from app.services.ai_analyst import answer_analytics, build_dashboard

router = APIRouter(tags=["analytics"])


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    return build_dashboard(db)


@router.post("/ai/chat", response_model=AiChatResponse)
def ai_chat(payload: AiChatRequest, db: Session = Depends(get_db)):
    return answer_analytics(db, payload.message)


@router.get("/reports/summary")
def reports_summary(db: Session = Depends(get_db)):
    dash = build_dashboard(db)
    return {
        "kpis": {
            "pipeline_value": dash.pipeline_value,
            "weighted_pipeline": dash.weighted_pipeline,
            "win_rate": dash.win_rate,
            "avg_deal_size": dash.avg_deal_size,
            "won_this_month": dash.won_this_month,
            "new_leads": dash.new_leads,
        },
        "stage_breakdown": dash.stage_breakdown,
        "revenue_trend": dash.revenue_trend,
        "top_owners": dash.top_owners,
        "health_alerts": dash.health_alerts,
    }
