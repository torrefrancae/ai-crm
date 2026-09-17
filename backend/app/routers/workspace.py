from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Activity, Message, Task
from app.schemas import ActivityOut, MessageOut, TaskCreate, TaskOut

router = APIRouter(tags=["workspace"])


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.due_date.asc().nullslast()).all()


@router.post("/tasks", response_model=TaskOut)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskCreate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    for key, value in payload.model_dump().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.get("/activities", response_model=list[ActivityOut])
def list_activities(db: Session = Depends(get_db)):
    rows = db.query(Activity).order_by(Activity.occurred_at.desc()).limit(100).all()
    out: list[ActivityOut] = []
    for a in rows:
        out.append(
            ActivityOut(
                id=a.id,
                kind=a.kind,
                subject=a.subject,
                body=a.body,
                contact_id=a.contact_id,
                deal_id=a.deal_id,
                owner=a.owner,
                occurred_at=a.occurred_at,
                contact_name=(
                    f"{a.contact.first_name} {a.contact.last_name}" if a.contact else None
                ),
            )
        )
    return out


@router.get("/inbox", response_model=list[MessageOut])
def list_inbox(db: Session = Depends(get_db)):
    return db.query(Message).order_by(Message.created_at.desc()).all()


@router.post("/inbox/{message_id}/read", response_model=MessageOut)
def mark_read(message_id: int, db: Session = Depends(get_db)):
    msg = db.get(Message, message_id)
    if not msg:
        raise HTTPException(404, "Message not found")
    msg.unread = 0
    db.commit()
    db.refresh(msg)
    return msg
