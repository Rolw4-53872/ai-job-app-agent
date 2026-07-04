import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Job Application Agent"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = "supersecretkeychangeinproduction"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/job_agent"
    
    # OpenAI / LLM
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"  # Fallback to gpt-4o or compatible
    
    # Gmail API (OAuth 2.0 Credentials)
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None
    GMAIL_REDIRECT_URI: str = "http://localhost:8000/api/gmail/callback"
    GMAIL_TOKEN_PATH: str = "token.json"
    
    # WhatsApp Cloud API
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_RECIPIENT_PHONE: Optional[str] = None  # The user's phone number to send alerts to
    
    # n8n Integration
    N8N_WEBHOOK_URL: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Sandbox / Mock Mode
    MOCK_MODE: bool = True  # If true, runs Gmail/WhatsApp/OpenAI in mock mode
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
