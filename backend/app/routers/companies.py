from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Company
from app.schemas import CompanyCreate, CompanyOut

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(q: str | None = None, db: Session = Depends(get_db)):
    rows = db.query(Company).order_by(Company.name.asc()).all()
    if q:
        needle = q.lower()
        rows = [c for c in rows if needle in f"{c.name} {c.industry} {c.city}".lower()]
    return rows


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    c = db.get(Company, company_id)
    if not c:
        raise HTTPException(404, "Company not found")
    return c


@router.post("", response_model=CompanyOut)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    c = Company(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.patch("/{company_id}", response_model=CompanyOut)
def update_company(company_id: int, payload: CompanyCreate, db: Session = Depends(get_db)):
    c = db.get(Company, company_id)
    if not c:
        raise HTTPException(404, "Company not found")
    for key, value in payload.model_dump().items():
        setattr(c, key, value)
    db.commit()
    db.refresh(c)
    return c
