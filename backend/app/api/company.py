from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.schemas import CompanyResponse, CompanyResearchRequest
from app.models.models import User, Company, ActivityLog
from app.api.deps import get_current_user
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/research", response_model=CompanyResponse)
async def research_company(
    request: CompanyResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Research a company by name and website, create/update its DB record."""
    # Check if company already exists by name
    company = db.query(Company).filter(Company.name.ilike(request.name)).first()
    
    # Perform research using LLM
    research_data = await AIService.research_company(request.name, request.website)
    
    if company:
        # Update existing
        company.website = request.website or company.website
        company.description = research_data.get("description", company.description)
        company.industry = research_data.get("industry", company.industry)
        company.products = research_data.get("products", company.products)
        company.technologies = research_data.get("technologies", company.technologies)
        company.career_page = research_data.get("career_page", company.career_page)
        company.hiring_email = research_data.get("hiring_email", company.hiring_email)
        company.hr_contact = research_data.get("hr_contact", company.hr_contact)
    else:
        # Create new
        company = Company(
            name=request.name,
            website=request.website or research_data.get("website"),
            description=research_data.get("description"),
            industry=research_data.get("industry"),
            products=research_data.get("products"),
            technologies=research_data.get("technologies"),
            career_page=research_data.get("career_page"),
            hiring_email=research_data.get("hiring_email"),
            hr_contact=research_data.get("hr_contact")
        )
        db.add(company)
        
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="company_research",
        details={"company_name": request.name, "industry": research_data.get("industry")}
    )
    db.add(log)
    
    db.commit()
    db.refresh(company)
    return company

@router.get("/", response_model=List[CompanyResponse])
def list_companies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all researched companies."""
    return db.query(Company).all()

@router.get("/{id}", response_model=CompanyResponse)
def get_company(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details for a single company."""
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
