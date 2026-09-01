from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AIIssueItem(BaseModel):
    title: str
    severity: str
    category: str
    why: str
    recommendation: str
    suggested_fix: Optional[str] = None


class AIAnalysisResponse(BaseModel):
    id: str
    test_run_id: str
    summary: str
    issues_analysis: List[Dict[str, Any]]
    priority_actions: List[str]
    model_used: str
    created_at: datetime

    class Config:
        from_attributes = True
