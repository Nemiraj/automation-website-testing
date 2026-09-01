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
    selector: Optional[str] = None
    viewport: Optional[str] = None
    status: str = "open"
    evidence: Optional[Dict[str, Any]] = Field(default_factory=dict)
    screenshot_url: Optional[str] = None


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
