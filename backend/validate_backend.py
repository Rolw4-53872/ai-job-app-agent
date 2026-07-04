import sys
import os

# Add the current directory to sys.path so we can import 'app'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("Starting validation of backend imports...")

try:
    from app.core.config import settings
    print("✓ Config settings imported successfully.")
    
    from app.core.database import engine, Base, get_db
    print("✓ Database engine and Base imported successfully.")
    
    from app.core.security import verify_password, get_password_hash, create_access_token
    print("✓ Security utils imported successfully.")
    
    from app.models.models import User, Profile, Resume, Company, Job, Application, Email, Reply, Notification, ActivityLog
    print("✓ DB Models imported successfully.")
    
    from app.schemas.schemas import UserCreate, UserResponse, ProfileResponse, CompanyResponse, JobResponse, ApplicationResponse, EmailResponse, ReplyResponse
    print("✓ Pydantic Schemas imported successfully.")
    
    from app.services.ai_service import AIService
    from app.services.gmail_service import GmailService
    from app.services.whatsapp_service import WhatsAppService
    from app.services.job_search_service import JobSearchService
    print("✓ Services (AI, Gmail, WhatsApp, Job Search) imported successfully.")
    
    from app.api import auth, profile, company, job, application, email, replies, assistant, dashboard, gmail_oauth
    print("✓ API Routers imported successfully.")
    
    from app.main import app
    print("✓ FastAPI app initialized successfully.")
    
    print("\n🎉 SUCCESS: All backend modules and imports resolved without syntax errors!")
except Exception as e:
    print(f"\n❌ ERROR: Import validation failed: {str(e)}")
    sys.exit(1)
