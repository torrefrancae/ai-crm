from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    industry: Mapped[str] = mapped_column(String(80), default="Technology")
    size: Mapped[str] = mapped_column(String(40), default="51-200")
    website: Mapped[str] = mapped_column(String(200), default="")
    city: Mapped[str] = mapped_column(String(80), default="")
    country: Mapped[str] = mapped_column(String(80), default="Philippines")
    annual_revenue: Mapped[float] = mapped_column(Float, default=0)
    health_score: Mapped[int] = mapped_column(Integer, default=70)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    contacts: Mapped[list["Contact"]] = relationship(back_populates="company")
    deals: Mapped[list["Deal"]] = relationship(back_populates="company")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(40), default="")
    title: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(40), default="active")
    owner: Mapped[str] = mapped_column(String(80), default="Alex Rivera")
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id"), nullable=True)
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped[Optional[Company]] = relationship(back_populates="contacts")
    deals: Mapped[list["Deal"]] = relationship(back_populates="contact")
    activities: Mapped[list["Activity"]] = relationship(back_populates="contact")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(160))
    company_name: Mapped[str] = mapped_column(String(160), default="")
    source: Mapped[str] = mapped_column(String(80), default="Website")
    status: Mapped[str] = mapped_column(String(40), default="new")
    score: Mapped[int] = mapped_column(Integer, default=50)
    owner: Mapped[str] = mapped_column(String(80), default="Alex Rivera")
    estimated_value: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    stage: Mapped[str] = mapped_column(String(40), default="qualification", index=True)
    amount: Mapped[float] = mapped_column(Float, default=0)
    probability: Mapped[int] = mapped_column(Integer, default=20)
    close_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    owner: Mapped[str] = mapped_column(String(80), default="Alex Rivera")
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id"), nullable=True)
    contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped[Optional[Company]] = relationship(back_populates="deals")
    contact: Mapped[Optional[Contact]] = relationship(back_populates="deals")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="todo")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    owner: Mapped[str] = mapped_column(String(80), default="Alex Rivera")
    related_type: Mapped[str] = mapped_column(String(40), default="deal")
    related_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(40), default="note")
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, default="")
    contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    deal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("deals.id"), nullable=True)
    owner: Mapped[str] = mapped_column(String(80), default="Alex Rivera")
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    contact: Mapped[Optional[Contact]] = relationship(back_populates="activities")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread: Mapped[str] = mapped_column(String(120), index=True)
    direction: Mapped[str] = mapped_column(String(20), default="inbound")
    from_name: Mapped[str] = mapped_column(String(120))
    subject: Mapped[str] = mapped_column(String(200))
    preview: Mapped[str] = mapped_column(Text, default="")
    unread: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
