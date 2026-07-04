from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.schemas import JobImportRequest, ApplicationResponse
from app.models.models import User, Company, Job, Application, ActivityLog
from app.api.deps import get_current_user
from app.services.job_search_service import JobSearchService
from app.services.ai_service import AIService

router = APIRouter()

@router.get("/search")
async def search_jobs(
    query: Optional[str] = None,
    country: Optional[str] = None,
    workplace_type: Optional[str] = None,
    job_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Search job listings from multiple sources using filters."""
    jobs = await JobSearchService.search_jobs(
        query=query,
        country=country,
        workplace_type=workplace_type,
        job_type=job_type
    )
    return jobs

@router.post("/import", response_model=ApplicationResponse)
async def import_job_as_application(
    request: JobImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import a job posting. 
    1. Research/upsert the company
    2. Create the job posting in DB
    3. Create an application instance in status 'Draft'
    """
    # 1. Check or create Company
    company = db.query(Company).filter(Company.name.ilike(request.company_name)).first()
    if not company:
        # Fetch company details
        research_data = await AIService.research_company(request.company_name, request.company_website)
        company = Company(
            name=request.company_name,
            website=request.company_website or research_data.get("website"),
            description=research_data.get("description"),
            industry=research_data.get("industry"),
            products=research_data.get("products"),
            technologies=research_data.get("technologies"),
            career_page=research_data.get("career_page"),
            hiring_email=research_data.get("hiring_email"),
            hr_contact=research_data.get("hr_contact")
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        
    # 2. Create Job
    job = Job(
        company_id=company.id,
        title=request.title,
        description=request.description,
        location=request.location,
        workplace_type=request.workplace_type,
        source=request.source or "Imported",
        url=request.url
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # 3. Create Application (defaulting to Draft status)
    application = Application(
        user_id=current_user.id,
        company_id=company.id,
        job_id=job.id,
        status="Draft"
    )
    db.add(application)
    
    # 4. Log action
    log = ActivityLog(
        user_id=current_user.id,
        action="job_imported",
        details={"company": company.name, "title": job.title}
    )
    db.add(log)
    
    db.commit()
    db.refresh(application)
    return application
