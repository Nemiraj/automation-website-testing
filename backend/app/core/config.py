import os
from typing import List, Dict, Any

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    try:
        from pydantic.v1 import BaseSettings, Field
    except ImportError:
        from pydantic import BaseModel as BaseSettings, Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Website Automation Testing Platform"
    API_V1_STR: str = "/api"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/websitetester"
    )
    DATABASE_SYNC_URL: str = os.getenv(
        "DATABASE_SYNC_URL",
        "postgresql://postgres:postgres@localhost:5432/websitetester"
    )
    
    # Redis & Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    
    # Storage
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./storage")
    MAX_SCREENSHOT_SIZE_MB: int = 10
    
    # Security & SSRF Protection
    ALLOW_INTERNAL_NETWORKS: bool = os.getenv("ALLOW_INTERNAL_NETWORKS", "false").lower() == "true"
    ALLOW_LOCALHOST_TESTING: bool = os.getenv("ALLOW_LOCALHOST_TESTING", "true").lower() == "true"
    LOCALHOST_HOST: str = os.getenv("LOCALHOST_HOST", "localhost")
    LOCALHOST_TIMEOUT: int = int(os.getenv("LOCALHOST_TIMEOUT", "30000"))
    MAX_PAGES_LIMIT: int = 100
    DEFAULT_MAX_PAGES: int = 10
    DEFAULT_TIMEOUT_MS: int = 30000
    CRAWL_MAX_DEPTH: int = 3
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Form Testing Safety
    ENABLE_FORM_SUBMISSION: bool = os.getenv("ENABLE_FORM_SUBMISSION", "false").lower() == "true"
    FORM_SUBMISSION_MODE: str = os.getenv("FORM_SUBMISSION_MODE", "validation_only")
    
    # AI Engine
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-1.5-pro")
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Standard Viewports
    VIEWPORTS: Dict[str, Dict[str, Any]] = {
        "desktop_large": {"width": 1920, "height": 1080, "label": "Desktop Large (1920x1080)"},
        "desktop_standard": {"width": 1366, "height": 768, "label": "Desktop Standard (1366x768)"},
        "tablet": {"width": 768, "height": 1024, "label": "Tablet Portrait (768x1024)"},
        "mobile_large": {"width": 390, "height": 844, "label": "Mobile Large (390x844)"},
        "mobile_standard": {"width": 375, "height": 812, "label": "Mobile Standard (375x812)"}
    }
    
    # Category Scoring Weights
    SCORE_WEIGHTS: Dict[str, float] = {
        "ui": 0.20,
        "responsive": 0.20,
        "functional": 0.15,
        "forms": 0.15,
        "accessibility": 0.15,
        "performance": 0.15
    }

    class Config:
        case_sensitive = True
        extra = "allow"


settings = Settings()

# Ensure local storage path exists
os.makedirs(settings.STORAGE_PATH, exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "screenshots"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "diffs"), exist_ok=True)
