from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, schemas, crud
from .database import engine, get_db
from .services.groq_ai import qualify_lead
from .services.fraud_detection import detect_fraud
from .services.email_service import send_hot_lead_notification

# ✅ AUTO-CREATE DATABASE TABLES
print("=" * 60)
print("Starting Lead Qualification API")
print("Initializing database...")
try:
    models.Base.metadata.create_all(bind=engine)
    print("✅ Database tables ready!")
except Exception as e:
    print(f"⚠️  Database initialization warning: {e}")
print("=" * 60)

app = FastAPI(
    title="Lead Qualification API",
    description="AI-powered lead qualification system",
    version="1.0.0"
)

# CORS middleware (allow Streamlit frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ CORRECT WAY - Use api_route with methods parameter
@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    """Health check endpoint - supports both GET and HEAD"""
    return {
        "status": "healthy",
        "message": "Lead Qualification API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Alternative health check endpoint"""
    return {"status": "ok"}


@app.post("/api/leads", response_model=schemas.LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    """
    Create a new lead.
    
    Steps:
    1. Validate input
    2. Check for fraud
    3. Qualify with AI
    4. Save to database
    5. Send email if hot lead
    """
    
    # Check for fraud
    fraud_check = detect_fraud(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        message=lead.initial_message
    )
    
    if fraud_check['is_fraud']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Submission flagged: {', '.join(fraud_check['signals'])}"
        )
    
    # Qualify with AI
    qualification = qualify_lead(lead.initial_message)
    
    # Save to database
    db_lead = crud.create_lead(
        db=db,
        lead=lead,
        qualification=qualification,
        fraud_check=fraud_check
    )
    
    # Send email notification if hot lead
    if qualification['quality_score'] >= 70:
        send_hot_lead_notification({
            'name': lead.name,
            'email': lead.email,
            'phone': lead.phone,
            'message': lead.initial_message,
            'goal': qualification['goal'],
            'timeline': qualification['timeline'],
            'budget_range': qualification['budget_range'],
            'quality_score': qualification['quality_score']
        })
    
    return db_lead


@app.get("/api/leads", response_model=List[schemas.LeadResponse])
def get_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all leads with optional filters"""
    
    leads = crud.get_leads(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        min_score=min_score,
        max_score=max_score
    )
    
    return leads


@app.get("/api/leads/{lead_id}", response_model=schemas.LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get single lead by ID"""
    
    lead = crud.get_lead(db=db, lead_id=lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@app.patch("/api/leads/{lead_id}", response_model=schemas.LeadResponse)
def update_lead(lead_id: int, lead_update: schemas.LeadUpdate, db: Session = Depends(get_db)):
    """Update lead status/assignment"""
    
    lead = crud.update_lead(db=db, lead_id=lead_id, lead_update=lead_update)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    return crud.get_lead_stats(db=db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)