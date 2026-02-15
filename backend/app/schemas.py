from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class LeadCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    initial_message: str = Field(..., min_length=10)
    source: Optional[str] = 'web'


class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    initial_message: str
    goal: Optional[str]
    timeline: Optional[str]
    budget_range: Optional[str]
    quality_score: Optional[int]
    is_fraud: bool
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LeadQualification(BaseModel):
    goal: str
    timeline: str
    budget_range: str
    quality_score: int


class FraudCheck(BaseModel):
    is_fraud: bool
    signals: list[str]


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None