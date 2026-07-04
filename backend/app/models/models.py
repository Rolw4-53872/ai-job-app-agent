import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Text, JSON, Uuid, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    country = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    skills = Column(JSON, default=list)  # list of strings
    education = Column(JSON, default=list)  # list of dicts
    certifications = Column(JSON, default=list)  # list of strings
    languages = Column(JSON, default=list)  # list of strings
    years_of_experience = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="profile")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)
    parsed_info = Column(JSON, default=dict)  # structured AI extraction results
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="resumes")

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    website = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    industry = Column(String, nullable=True)
    products = Column(JSON, default=list)  # list of strings/dicts
    technologies = Column(JSON, default=list)  # list of strings
    career_page = Column(String, nullable=True)
    hiring_email = Column(String, nullable=True)
    hr_contact = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="company", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(Uuid(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)  # Country/City
    workplace_type = Column(String, default="Remote")  # Remote, Hybrid, On-site
    source = Column(String, nullable=True)  # LinkedIn, Indeed, etc.
    url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Uuid(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Uuid(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, default="Draft")  # Draft, Ready, Approved, Sent, Delivered, Replied, Interview, Assessment, Offer, Rejected, Closed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="applications")
    company = relationship("Company", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    emails = relationship("Email", back_populates="application", cascade="all, delete-orphan")
    replies = relationship("Reply", back_populates="application", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="application", cascade="all, delete-orphan")

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(Uuid(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    recipient_email = Column(String, nullable=False)
    gmail_message_id = Column(String, nullable=True)
    status = Column(String, default="Draft")  # Draft, Pending_Approval, Approved, Sent, Failed
    rationale = Column(Text, nullable=True)  # Explanation of why the email was written this way
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    
    application = relationship("Application", back_populates="emails")

class Reply(Base):
    __tablename__ = "replies"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(Uuid(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    gmail_message_id = Column(String, unique=True, nullable=False)
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    classification = Column(String, nullable=False)  # Interview invitation, Assessment, Need more info, Acceptance, Rejection, General inquiry, Automatic response
    summary = Column(Text, nullable=True)
    priority = Column(String, default="Low")  # Low, Medium, High, Urgent
    suggested_reply = Column(Text, nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    application = relationship("Application", back_populates="replies")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    application_id = Column(Uuid(as_uuid=True), ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    type = Column(String, default="WhatsApp")  # WhatsApp, System
    recipient = Column(String, nullable=False)  # Phone number or email
    content = Column(Text, nullable=False)
    sent_status = Column(String, default="Pending")  # Pending, Sent, Failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")
    application = relationship("Application", back_populates="notifications")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="activity_logs")
