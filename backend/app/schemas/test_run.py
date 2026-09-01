from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class TestConfig(BaseModel):
    max_pages: int = Field(default=10, ge=1, le=100)
    timeout_ms: int = Field(default=30000, ge=5000, le=120000)
    viewports: List[str] = Field(
        default=["desktop_large", "tablet", "mobile_large"]
    )
    # Feature toggles
    enable_ui: bool = True
    enable_responsive: bool = True
    enable_links: bool = True
    enable_images: bool = True
    enable_javascript: bool = True
    enable_forms: bool = True
    enable_accessibility: bool = True
    enable_performance: bool = True
    enable_screenshots: bool = True
    enable_ai: bool = True
    
    # Form submission config
    form_submission_mode: str = "validation_only"  # validation_only | synthetic_submit


class TestRunCreate(BaseModel):
    project_id: Optional[str] = None
    target_url: str
    config: Optional[TestConfig] = Field(default_factory=TestConfig)


class TestRunStatusResponse(BaseModel):
    id: str
    target_url: str
    status: str
    progress_percentage: int
    current_stage: str
    current_page_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TestRunResponse(TestRunStatusResponse):
    project_id: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Scores
    overall_score: Optional[float] = None
    ui_score: Optional[float] = None
    responsive_score: Optional[float] = None
    functional_score: Optional[float] = None
    forms_score: Optional[float] = None
    accessibility_score: Optional[float] = None
    performance_score: Optional[float] = None
    
    # Counts
    total_pages_scanned: int = 0
    critical_issues_count: int = 0
    high_issues_count: int = 0
    medium_issues_count: int = 0
    low_issues_count: int = 0
    info_issues_count: int = 0

    class Config:
        from_attributes = True
