from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.schemas import ApplicationResponse, ApplicationCreate, ApplicationUpdate
from app.models.models import User, Company, Job, Application, ActivityLog
from app.api.deps import get_current_user
from app.services.ai_service import AIService

router = APIRouter()

@router.get("/", response_model=List[ApplicationResponse])
def list_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all job applications for the current user."""
    return db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.updated_at.desc()).all()

@router.get("/{id}", response_model=ApplicationResponse)
def get_application(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details for a single application."""
    application = db.query(Application).filter(
        Application.id == id,
        Application.user_id == current_user.id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

@router.post("/", response_model=ApplicationResponse)
async def create_application(
    request: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job application (usually in Draft status)."""
    # Verify company exists
    company = db.query(Company).filter(Company.id == request.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found. Research the company first.")
        
    application = Application(
        user_id=current_user.id,
        company_id=request.company_id,
        job_id=request.job_id,
        status=request.status,
        notes=request.notes
    )
    db.add(application)
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="application_created",
        details={"company": company.name, "status": request.status}
    )
    db.add(log)
    
    db.commit()
    db.refresh(application)
    return application

@router.put("/{id}", response_model=ApplicationResponse)
def update_application(
    id: str,
    request: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update application details like status or notes."""
    application = db.query(Application).filter(
        Application.id == id,
        Application.user_id == current_user.id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
        
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="application_status_update",
        details={"application_id": id, "new_status": application.status}
    )
    db.add(log)
    
    db.commit()
    db.refresh(application)
    return application
