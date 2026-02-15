from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional


def create_lead(db: Session, lead: schemas.LeadCreate, qualification: dict, fraud_check: dict) -> models.Lead:
    """Create a new lead in database"""
    
    db_lead = models.Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        initial_message=lead.initial_message,
        source=lead.source,
        goal=qualification.get('goal'),
        timeline=qualification.get('timeline'),
        budget_range=qualification.get('budget_range'),
        quality_score=qualification.get('quality_score'),
        is_fraud=fraud_check.get('is_fraud', False),
        fraud_signals=str(fraud_check.get('signals', []))
    )
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    return db_lead


def get_lead(db: Session, lead_id: int) -> Optional[models.Lead]:
    """Get single lead by ID"""
    return db.query(models.Lead).filter(models.Lead.id == lead_id).first()


def get_leads(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None
) -> List[models.Lead]:
    """Get leads with filters"""
    
    query = db.query(models.Lead)
    
    if status:
        query = query.filter(models.Lead.status == status)
    
    if min_score is not None:
        query = query.filter(models.Lead.quality_score >= min_score)
    
    if max_score is not None:
        query = query.filter(models.Lead.quality_score <= max_score)
    
    return query.order_by(models.Lead.created_at.desc()).offset(skip).limit(limit).all()


def update_lead(db: Session, lead_id: int, lead_update: schemas.LeadUpdate) -> Optional[models.Lead]:
    """Update lead status/assignment"""
    
    db_lead = get_lead(db, lead_id)
    if not db_lead:
        return None
    
    update_data = lead_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_lead, field, value)
    
    db.commit()
    db.refresh(db_lead)
    
    return db_lead


def get_lead_stats(db: Session) -> dict:
    """Get dashboard statistics"""
    
    total = db.query(models.Lead).count()
    hot = db.query(models.Lead).filter(models.Lead.quality_score >= 70).count()
    warm = db.query(models.Lead).filter(
        models.Lead.quality_score >= 40,
        models.Lead.quality_score < 70
    ).count()
    cold = db.query(models.Lead).filter(models.Lead.quality_score < 40).count()
    fraud = db.query(models.Lead).filter(models.Lead.is_fraud == True).count()
    
    return {
        'total': total,
        'hot': hot,
        'warm': warm,
        'cold': cold,
        'fraud': fraud
    }