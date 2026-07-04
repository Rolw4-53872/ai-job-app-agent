from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

# Profile Schemas
class ProfileBase(BaseModel):
    full_name: str
    phone_number: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: List[str] = []
    education: List[Dict[str, Any]] = []
    certifications: List[str] = []
    languages: List[str] = []
    years_of_experience: float = 0.0

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: Optional[List[str]] = None
    education: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    years_of_experience: Optional[float] = None

class ProfileResponse(ProfileBase):
    id: UUID
    user_id: UUID
    updated_at: datetime
    class Config:
        from_attributes = True

# Resume Schemas
class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    file_name: str
    file_path: str
    parsed_info: Dict[str, Any]
    created_at: datetime
    class Config:
        from_attributes = True

# Company Schemas
class CompanyBase(BaseModel):
    name: str
    website: Optional[str] = None

class CompanyResearchRequest(BaseModel):
    name: str
    website: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: UUID
    description: Optional[str] = None
    industry: Optional[str] = None
    products: List[Any] = []
    technologies: List[str] = []
    career_page: Optional[str] = None
    hiring_email: Optional[str] = None
    hr_contact: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# Job Schemas
class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    workplace_type: str = "Remote"
    source: Optional[str] = None
    url: Optional[str] = None

class JobImportRequest(BaseModel):
    company_name: str
    company_website: Optional[str] = None
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    workplace_type: str = "Remote"
    source: Optional[str] = None
    url: Optional[str] = None

class JobResponse(JobBase):
    id: UUID
    company_id: UUID
    company_name: Optional[str] = None  # populated dynamically
    created_at: datetime
    class Config:
        from_attributes = True

# Application Schemas
class ApplicationCreate(BaseModel):
    company_id: UUID
    job_id: Optional[UUID] = None
    status: str = "Draft"
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    company_id: UUID
    company: CompanyResponse
    job_id: Optional[UUID] = None
    job: Optional[JobResponse] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# Email Schemas
class EmailGenerateRequest(BaseModel):
    application_id: UUID

class EmailRegenerateRequest(BaseModel):
    style: str  # bold, professional, warm, concise, technical
    additional_instructions: Optional[str] = None

class EmailResponse(BaseModel):
    id: UUID
    application_id: UUID
    subject: str
    body: str
    recipient_email: str
    gmail_message_id: Optional[str] = None
    status: str
    rationale: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# Reply Schemas
class ReplyResponse(BaseModel):
    id: UUID
    application_id: UUID
    gmail_message_id: str
    sender: str
    subject: str
    body: str
    classification: str
    summary: Optional[str] = None
    priority: str
    suggested_reply: Optional[str] = None
    processed_at: datetime
    class Config:
        from_attributes = True

class ReplyWebhookInput(BaseModel):
    gmail_message_id: str
    sender: str
    subject: str
    body: str

# Notification Schemas
class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    application_id: Optional[UUID] = None
    type: str
    recipient: str
    content: str
    sent_status: str
    created_at: datetime
    class Config:
        from_attributes = True

# Activity Log Schemas
class ActivityLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    details: Dict[str, Any]
    created_at: datetime
    class Config:
        from_attributes = True

# AI Assistant Schemas
class AssistantChatRequest(BaseModel):
    message: str

class AssistantChatResponse(BaseModel):
    response: str
    suggested_actions: List[Dict[str, Any]] = []

# Dashboard Stats Schemas
class StatusCount(BaseModel):
    status: str
    count: int

class ActivityCount(BaseModel):
    month: str
    applications_sent: int
    interviews: int

class DashboardStatsResponse(BaseModel):
    total_applications: int
    interviews_count: int
    pending_replies: int
    rejected_count: int
    offers_count: int
    status_distribution: List[StatusCount]
    monthly_activity: List[ActivityCount]
    recent_activities: List[ActivityLogResponse]
