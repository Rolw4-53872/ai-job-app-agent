import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, profile, company, job, application, email, replies, assistant, dashboard, gmail_oauth

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

import time

# Create DB tables if they don't exist (with retry loop for database readiness)
for i in range(15):
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables verified/created successfully.")
        break
    except Exception as e:
        logging.warning(f"Database connection attempt {i+1}/15 failed: {str(e)}")
        time.sleep(3)
else:
    logging.error("Failed to connect to database after 15 attempts. Proceeding with caution.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for managing AI-driven job applications under human control.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(profile.router, prefix=f"{settings.API_V1_STR}/profile", tags=["Profile & Resume"])
app.include_router(company.router, prefix=f"{settings.API_V1_STR}/companies", tags=["Company Research"])
app.include_router(job.router, prefix=f"{settings.API_V1_STR}/jobs", tags=["Job Search"])
app.include_router(application.router, prefix=f"{settings.API_V1_STR}/applications", tags=["Applications Pipeline"])
app.include_router(email.router, prefix=f"{settings.API_V1_STR}/emails", tags=["Personalized Emails"])
app.include_router(replies.router, prefix=f"{settings.API_V1_STR}/replies", tags=["Recruiter Replies"])
app.include_router(assistant.router, prefix=f"{settings.API_V1_STR}/assistant", tags=["AI Chat Assistant"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard Statistics"])
app.include_router(gmail_oauth.router, prefix=settings.API_V1_STR, tags=["Gmail OAuth"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "docs_url": "/docs"
    }
