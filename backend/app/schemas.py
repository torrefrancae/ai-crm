from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CompanyOut(OrmModel):
    id: int
    name: str
    industry: str
    size: str
    website: str
    city: str
    country: str
    annual_revenue: float
    health_score: int
    created_at: datetime


class CompanyCreate(BaseModel):
    name: str
    industry: str = "Technology"
    size: str = "51-200"
    website: str = ""
    city: str = ""
    country: str = "Philippines"
    annual_revenue: float = 0
    health_score: int = 70


class ContactOut(OrmModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    title: str
    status: str
    owner: str
    company_id: Optional[int]
    last_contacted_at: Optional[datetime]
    created_at: datetime
    company_name: Optional[str] = None


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    title: str = ""
    status: str = "active"
    owner: str = "Alex Rivera"
    company_id: Optional[int] = None


class LeadOut(OrmModel):
    id: int
    name: str
    email: str
    company_name: str
    source: str
    status: str
    score: int
    owner: str
    estimated_value: float
    notes: str
    created_at: datetime


class LeadCreate(BaseModel):
    name: str
    email: str
    company_name: str = ""
    source: str = "Website"
    status: str = "new"
    score: int = 50
    owner: str = "Alex Rivera"
    estimated_value: float = 0
    notes: str = ""


class DealOut(OrmModel):
    id: int
    title: str
    stage: str
    amount: float
    probability: int
    close_date: Optional[datetime]
    owner: str
    company_id: Optional[int]
    contact_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    company_name: Optional[str] = None
    contact_name: Optional[str] = None


class DealCreate(BaseModel):
    title: str
    stage: str = "qualification"
    amount: float = 0
    probability: int = 20
    close_date: Optional[datetime] = None
    owner: str = "Alex Rivera"
    company_id: Optional[int] = None
    contact_id: Optional[int] = None


class DealStageUpdate(BaseModel):
    stage: str
    probability: Optional[int] = None


class TaskOut(OrmModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    due_date: Optional[datetime]
    owner: str
    related_type: str
    related_id: Optional[int]
    created_at: datetime


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[datetime] = None
    owner: str = "Alex Rivera"
    related_type: str = "deal"
    related_id: Optional[int] = None


class ActivityOut(OrmModel):
    id: int
    kind: str
    subject: str
    body: str
    contact_id: Optional[int]
    deal_id: Optional[int]
    owner: str
    occurred_at: datetime
    contact_name: Optional[str] = None


class MessageOut(OrmModel):
    id: int
    thread: str
    direction: str
    from_name: str
    subject: str
    preview: str
    unread: int
    created_at: datetime


class DashboardOut(BaseModel):
    pipeline_value: float
    weighted_pipeline: float
    open_deals: int
    won_this_month: float
    new_leads: int
    tasks_due: int
    avg_deal_size: float
    win_rate: float
    stage_breakdown: list[dict]
    revenue_trend: list[dict]
    top_owners: list[dict]
    health_alerts: list[dict]


class AiChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class AiChatResponse(BaseModel):
    reply: str
    insights: list[str]
    suggested_actions: list[str]
