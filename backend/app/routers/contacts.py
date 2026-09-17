from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Company, Contact
from app.schemas import ContactCreate, ContactOut

router = APIRouter(prefix="/contacts", tags=["contacts"])


def serialize(c: Contact) -> ContactOut:
    return ContactOut(
        id=c.id,
        first_name=c.first_name,
        last_name=c.last_name,
        email=c.email,
        phone=c.phone,
        title=c.title,
        status=c.status,
        owner=c.owner,
        company_id=c.company_id,
        last_contacted_at=c.last_contacted_at,
        created_at=c.created_at,
        company_name=c.company.name if c.company else None,
    )


@router.get("", response_model=list[ContactOut])
def list_contacts(q: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Contact).order_by(Contact.last_name.asc())
    rows = query.all()
    if q:
        needle = q.lower()
        rows = [
            c
            for c in rows
            if needle in f"{c.first_name} {c.last_name} {c.email} {c.title}".lower()
        ]
    return [serialize(c) for c in rows]


@router.get("/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    c = db.get(Contact, contact_id)
    if not c:
        raise HTTPException(404, "Contact not found")
    return serialize(c)


@router.post("", response_model=ContactOut)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    if payload.company_id and not db.get(Company, payload.company_id):
        raise HTTPException(400, "Company not found")
    c = Contact(**payload.model_dump(), last_contacted_at=datetime.utcnow())
    db.add(c)
    db.commit()
    db.refresh(c)
    return serialize(c)


@router.patch("/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: int, payload: ContactCreate, db: Session = Depends(get_db)):
    c = db.get(Contact, contact_id)
    if not c:
        raise HTTPException(404, "Contact not found")
    for key, value in payload.model_dump().items():
        setattr(c, key, value)
    db.commit()
    db.refresh(c)
    return serialize(c)


@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    c = db.get(Contact, contact_id)
    if not c:
        raise HTTPException(404, "Contact not found")
    db.delete(c)
    db.commit()
    return {"ok": True}
