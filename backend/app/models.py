from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func
from .database import Base


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Contact Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    
    # Lead Details
    initial_message = Column(Text, nullable=False)
    
    # AI Qualification Results
    goal = Column(String(50), index=True)  # investment, retirement, etc.
    timeline = Column(String(50))
    budget_range = Column(String(50))
    quality_score = Column(Integer)
    
    # Fraud Detection
    is_fraud = Column(Boolean, default=False)
    fraud_signals = Column(Text)  # JSON string of signals
    
    # Status & Assignment
    status = Column(String(50), default='new', index=True)
    assigned_to = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Source tracking
    source = Column(String(100))  # web, referral, etc.
    ip_address = Column(String(45))


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default='admin')  # admin, advisor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LeadActivity(Base):
    __tablename__ = "lead_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, nullable=False, index=True)
    activity_type = Column(String(50))  # created, assigned, contacted, meeting_booked, closed
    description = Column(Text)
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())