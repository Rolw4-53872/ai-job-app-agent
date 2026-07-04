from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.schemas import EmailResponse, EmailGenerateRequest, EmailRegenerateRequest
from app.models.models import User, Application, Profile, Company, Job, Email, ActivityLog
from app.api.deps import get_current_user
from app.services.ai_service import AIService
from app.services.gmail_service import GmailService

router = APIRouter()

@router.get("/pending", response_model=List[EmailResponse])
def get_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all email drafts that are pending human approval."""
    return db.query(Email).join(Application).filter(
        Application.user_id == current_user.id,
        Email.status.in_(["Draft", "Pending_Approval"])
    ).order_by(Email.created_at.desc()).all()

@router.post("/generate", response_model=EmailResponse)
async def generate_email(
    request: EmailGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a personalized email for a job application.
    Reads candidate profile, company info, and job specs to construct a tailored draft.
    """
    application = db.query(Application).filter(
        Application.id == request.application_id,
        Application.user_id == current_user.id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
         raise HTTPException(status_code=400, detail="Applicant profile not found. Please set up profile first.")
         
    company = db.query(Company).filter(Company.id == application.company_id).first()
    job = db.query(Job).filter(Job.id == application.job_id).first() if application.job_id else None
    
    # Pack parameters for generation
    profile_data = {
        "full_name": profile.full_name,
        "email": current_user.email,
        "phone_number": profile.phone_number,
        "linkedin_url": profile.linkedin_url,
        "years_of_experience": profile.years_of_experience,
        "skills": profile.skills,
        "education": profile.education
    }
    
    company_data = {
        "name": company.name,
        "website": company.website,
        "description": company.description,
        "industry": company.industry,
        "products": company.products,
        "technologies": company.technologies,
        "hr_contact": company.hr_contact or "Hiring Manager"
    }
    
    job_data = {
        "title": job.title if job else "Software Engineer",
        "description": job.description if job else "Backend / AI Automation role",
        "workplace_type": job.workplace_type if job else "Remote"
    }
    
    recipient_email = company.hiring_email or f"jobs@{company.name.lower().replace(' ', '')}.com"
    
    # Generate draft using AI Service
    ai_draft = await AIService.generate_email(
        profile_data=profile_data,
        company_data=company_data,
        job_data=job_data,
        style="professional"
    )
    
    # Save draft in DB
    email_draft = Email(
        application_id=application.id,
        subject=ai_draft.get("subject", f"Job Application - {profile.full_name}"),
        body=ai_draft.get("body", ""),
        recipient_email=recipient_email,
        status="Draft",
        rationale=ai_draft.get("rationale", "")
    )
    db.add(email_draft)
    
    # Update application status
    application.status = "Ready"
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="email_draft_generated",
        details={"application_id": str(application.id), "company": company.name}
    )
    db.add(log)
    
    db.commit()
    db.refresh(email_draft)
    return email_draft

@router.post("/{id}/regenerate", response_model=EmailResponse)
async def regenerate_email(
    id: str,
    request: EmailRegenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate a draft email using a new tone/style and additional feedback comments."""
    email_draft = db.query(Email).join(Application).filter(
        Email.id == id,
        Application.user_id == current_user.id
    ).first()
    if not email_draft:
        raise HTTPException(status_code=404, detail="Email draft not found")
        
    if email_draft.status == "Sent":
        raise HTTPException(status_code=400, detail="Cannot regenerate an email that has already been sent.")
        
    application = email_draft.application
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    company = db.query(Company).filter(Company.id == application.company_id).first()
    job = db.query(Job).filter(Job.id == application.job_id).first() if application.job_id else None
    
    profile_data = {
        "full_name": profile.full_name,
        "email": current_user.email,
        "phone_number": profile.phone_number,
        "linkedin_url": profile.linkedin_url,
        "years_of_experience": profile.years_of_experience,
        "skills": profile.skills,
        "education": profile.education
    }
    
    company_data = {
        "name": company.name,
        "website": company.website,
        "description": company.description,
        "industry": company.industry,
        "products": company.products,
        "technologies": company.technologies,
        "hr_contact": company.hr_contact or "Hiring Manager"
    }
    
    job_data = {
        "title": job.title if job else "Software Engineer",
        "description": job.description if job else "Backend / AI Automation role",
        "workplace_type": job.workplace_type if job else "Remote"
    }
    
    # Regenerate draft
    ai_draft = await AIService.generate_email(
        profile_data=profile_data,
        company_data=company_data,
        job_data=job_data,
        style=request.style,
        additional_instructions=request.additional_instructions
    )
    
    # Update draft fields
    email_draft.subject = ai_draft.get("subject", email_draft.subject)
    email_draft.body = ai_draft.get("body", email_draft.body)
    email_draft.rationale = ai_draft.get("rationale", email_draft.rationale)
    email_draft.status = "Draft"
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="email_draft_regenerated",
        details={"email_id": id, "style": request.style}
    )
    db.add(log)
    
    db.commit()
    db.refresh(email_draft)
    return email_draft

@router.post("/{id}/approve", response_model=EmailResponse)
def approve_email(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a draft email. Moves status to 'Approved'."""
    email_draft = db.query(Email).join(Application).filter(
        Email.id == id,
        Application.user_id == current_user.id
    ).first()
    if not email_draft:
        raise HTTPException(status_code=404, detail="Email draft not found")
        
    email_draft.status = "Approved"
    email_draft.application.status = "Approved"
    
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="email_approved",
        details={"email_id": id}
    )
    db.add(log)
    
    db.commit()
    db.refresh(email_draft)
    return email_draft

@router.post("/{id}/send", response_model=EmailResponse)
async def send_email(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send the approved email via Gmail API. 
    Strict requirement: Email must be approved first.
    """
    email_entry = db.query(Email).join(Application).filter(
        Email.id == id,
        Application.user_id == current_user.id
    ).first()
    if not email_entry:
        raise HTTPException(status_code=404, detail="Email entry not found")
        
    if email_entry.status != "Approved":
        raise HTTPException(
            status_code=400, 
            detail=f"Email cannot be sent. Current status is '{email_entry.status}'. You must Approve it first."
        )
        
    try:
        # Send via Gmail Service
        gmail_id = await GmailService.send_email(
            to=email_entry.recipient_email,
            subject=email_entry.subject,
            body=email_entry.body
        )
        
        # Update entry status
        email_entry.status = "Sent"
        email_entry.gmail_message_id = gmail_id
        email_entry.sent_at = datetime.utcnow()
        
        # Update application status
        email_entry.application.status = "Sent"
        
        # Log activity
        log = ActivityLog(
            user_id=current_user.id,
            action="email_sent",
            details={"email_id": id, "gmail_message_id": gmail_id, "recipient": email_entry.recipient_email}
        )
        db.add(log)
        
        db.commit()
        db.refresh(email_entry)
        return email_entry
    except Exception as e:
        email_entry.status = "Failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
