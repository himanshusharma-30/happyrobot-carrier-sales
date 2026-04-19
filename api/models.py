"""SQLAlchemy ORM models."""
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text

from api.db import Base


class Load(Base):
    __tablename__ = "loads"

    load_id = Column(String, primary_key=True)
    origin = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=False, index=True)
    pickup_datetime = Column(DateTime, nullable=False)
    delivery_datetime = Column(DateTime, nullable=False)
    equipment_type = Column(String, nullable=False, index=True)
    loadboard_rate = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    weight = Column(Integer, nullable=True)
    commodity_type = Column(String, nullable=True)
    num_of_pieces = Column(Integer, nullable=True)
    miles = Column(Integer, nullable=True)
    dimensions = Column(String, nullable=True)


class NegotiationState(Base):
    """Server-side per-call negotiation state so we can track rounds + last counter."""
    __tablename__ = "negotiation_state"

    call_id = Column(String, primary_key=True)
    load_id = Column(String, nullable=False)
    round_number = Column(Integer, default=0)
    last_counter = Column(Float, nullable=True)
    last_carrier_offer = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CallEvent(Base):
    __tablename__ = "call_events"

    call_id = Column(String, primary_key=True)
    mc_number = Column(String, nullable=True, index=True)
    carrier_name = Column(String, nullable=True)
    load_id = Column(String, nullable=True, index=True)
    loadboard_rate = Column(Float, nullable=True)
    final_rate = Column(Float, nullable=True)
    num_negotiation_rounds = Column(Integer, default=0)
    outcome = Column(String, nullable=True, index=True)
    sentiment = Column(String, nullable=True, index=True)
    transcript = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)