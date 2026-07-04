import os
import shutil
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pypdf import PdfReader
from app.core.database import get_db
from app.schemas.schemas import ProfileResponse, ProfileUpdate, ResumeResponse
from app.models.models import User, Profile, Resume, ActivityLog
from app.api.deps import get_current_user
from app.services.ai_service import AIService

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve current user profile."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/", response_model=ProfileResponse)
def update_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile fields."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
        
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="profile_update",
        details={"updated_fields": list(update_data.keys())}
    )
    db.add(log)
    
    db.commit()
    db.refresh(profile)
    return profile

@router.post("/resume", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload PDF resume, extract details using AI, and update user profile skills/experience."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resume files are accepted.")
        
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file.filename}")
    
    # Save the file locally
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Extract text from PDF
    extracted_text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
    except Exception as e:
        extracted_text = f"Error extracting text from PDF: {str(e)}"
        
    # Parse resume details using AI service
    parsed_info = await AIService.parse_resume(extracted_text)
    
    # Save/Update Resume entry
    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        extracted_text=extracted_text,
        parsed_info=parsed_info
    )
    db.add(resume)
    
    # Update candidate profile fields based on extraction
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile:
        profile.skills = parsed_info.get("skills", [])
        profile.languages = parsed_info.get("languages", [])
        
        # Merge experience titles if years_of_experience is parsed or estimated
        exp_list = parsed_info.get("experience", [])
        profile.years_of_experience = float(len(exp_list)) if exp_list else 0.0
        
        # Convert simple list of string experiences or dictionaries
        profile.education = parsed_info.get("education", [])
        
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="resume_uploaded",
        details={"file_name": file.filename, "extracted_skills_count": len(parsed_info.get("skills", []))}
    )
    db.add(log)
    
    db.commit()
    db.refresh(resume)
    return resume
