from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class IssueBase(BaseModel):
    page_url: str
    category: str
    severity: str
    title: str
    description: str
    why_it_matters: Optional[str] = None
    recommendation: Optional[str] = None
    suggested_fix: Optional[str] = None
    issue_number: Optional[int] = None
    section: Optional[str] = None
    selector: Optional[str] = None
    viewport: Optional[str] = None
    status: str = "open"
    coordinates: Optional[Dict[str, Any]] = Field(default_factory=dict)
    marker_type: Optional[str] = "rectangle"
    screenshot_url: Optional[str] = None
    annotated_screenshot_url: Optional[str] = None
    source_location: Optional[Dict[str, Any]] = Field(default_factory=dict)
    fix_confidence: Optional[str] = "high"
    fix_reasoning: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IssueCreate(IssueBase):
    test_run_id: str
    page_id: Optional[str] = None


class IssueUpdate(BaseModel):
    status: Optional[str] = None


class IssueResponse(IssueBase):
    id: str
    test_run_id: str
    page_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
