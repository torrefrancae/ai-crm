from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Deal
from app.schemas import DealCreate, DealOut, DealStageUpdate

router = APIRouter(prefix="/deals", tags=["deals"])


def serialize(d: Deal) -> DealOut:
    return DealOut(
        id=d.id,
        title=d.title,
        stage=d.stage,
        amount=d.amount,
        probability=d.probability,
        close_date=d.close_date,
        owner=d.owner,
        company_id=d.company_id,
        contact_id=d.contact_id,
        created_at=d.created_at,
        updated_at=d.updated_at,
        company_name=d.company.name if d.company else None,
        contact_name=(
            f"{d.contact.first_name} {d.contact.last_name}" if d.contact else None
        ),
    )


@router.get("", response_model=list[DealOut])
def list_deals(stage: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Deal).order_by(Deal.updated_at.desc())
    if stage:
        query = query.filter(Deal.stage == stage)
    return [serialize(d) for d in query.all()]


@router.post("", response_model=DealOut)
def create_deal(payload: DealCreate, db: Session = Depends(get_db)):
    d = Deal(**payload.model_dump(), updated_at=datetime.utcnow())
    db.add(d)
    db.commit()
    db.refresh(d)
    return serialize(d)


@router.patch("/{deal_id}/stage", response_model=DealOut)
def update_stage(deal_id: int, payload: DealStageUpdate, db: Session = Depends(get_db)):
    d = db.get(Deal, deal_id)
    if not d:
        raise HTTPException(404, "Deal not found")
    d.stage = payload.stage
    if payload.probability is not None:
        d.probability = payload.probability
    elif payload.stage == "closed_won":
        d.probability = 100
    elif payload.stage == "closed_lost":
        d.probability = 0
    d.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(d)
    return serialize(d)


@router.patch("/{deal_id}", response_model=DealOut)
def update_deal(deal_id: int, payload: DealCreate, db: Session = Depends(get_db)):
    d = db.get(Deal, deal_id)
    if not d:
        raise HTTPException(404, "Deal not found")
    for key, value in payload.model_dump().items():
        setattr(d, key, value)
    d.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(d)
    return serialize(d)
