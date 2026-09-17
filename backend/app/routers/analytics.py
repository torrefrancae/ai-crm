from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AiChatRequest, AiChatResponse, DashboardOut
from app.services.ai_analyst import answer_analytics, build_dashboard
from app.services.crm_cache import get_cached_answer, get_cached_context
from app.services.limit import (
    begin_flight,
    client_ip,
    deny_message,
    end_flight,
    peek_try,
    take_try,
    usage_for,
)

router = APIRouter(tags=["analytics"])
MESSAGE_MAX = 600


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    return build_dashboard(db)


@router.get("/usage")
def usage(request: Request):
    ip = client_ip(request)
    return {"ok": True, **usage_for(ip)}


@router.post("/ai/chat")
def ai_chat(payload: AiChatRequest, request: Request, db: Session = Depends(get_db)):
    ip = client_ip(request)
    message = (payload.message or "").strip()
    if not message:
        return JSONResponse(status_code=400, content={"error": "message required", **usage_for(ip)})
    if len(message) > MESSAGE_MAX:
        return JSONResponse(
            status_code=400,
            content={"error": f"Keep prompts under {MESSAGE_MAX} characters.", **usage_for(ip)},
        )

    _context, context_fp, _hit = get_cached_context(db)
    cached = get_cached_answer(message, context_fp)
    if cached is not None:
        body = cached.model_dump()
        body.update(usage_for(ip))
        body["cached"] = True
        return body

    gate = peek_try(ip)
    if not gate["ok"]:
        return JSONResponse(
            status_code=429,
            content={
                "error": deny_message(str(gate["reason"])),
                "code": gate["reason"],
                "used": gate["used"],
                "left": gate["left"],
                "max": gate["max"],
            },
        )

    if not begin_flight(ip):
        return JSONResponse(
            status_code=429,
            content={"error": deny_message("busy"), "code": "busy", **usage_for(ip)},
        )

    reserved = take_try(ip)
    if not reserved["ok"]:
        end_flight(ip)
        return JSONResponse(
            status_code=429,
            content={
                "error": deny_message(str(reserved["reason"])),
                "code": reserved["reason"],
                "used": reserved["used"],
                "left": reserved["left"],
                "max": reserved["max"],
            },
        )

    try:
        result: AiChatResponse = answer_analytics(db, message)
        body = result.model_dump()
        body.update(
            {
                "used": reserved["used"],
                "left": reserved["left"],
                "max": reserved["max"],
                "cached": False,
            }
        )
        return body
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "AI analyst failed.", **usage_for(ip)},
        )
    finally:
        end_flight(ip)


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
