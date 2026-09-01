from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.schemas.test_run import TestRunResponse
from backend.app.schemas.page import PageResponse
from backend.app.schemas.issue import IssueResponse
from backend.app.schemas.form import FormResponse
from backend.app.schemas.screenshot import ScreenshotResponse
from backend.app.schemas.ai_analysis import AIAnalysisResponse


class ScoreBreakdown(BaseModel):
    overall: float
    ui: float
    responsive: float
    functional: float
    forms: float
    accessibility: float
    performance: float


class IssuesCountBySeverity(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    total: int = 0


class IssuesCountByCategory(BaseModel):
    ui: int = 0
    responsive: int = 0
    functional: int = 0
    forms: int = 0
    accessibility: int = 0
    performance: int = 0
    javascript: int = 0
    network: int = 0
    visual_regression: int = 0


class TestReportResponse(BaseModel):
    test_run: TestRunResponse
    scores: ScoreBreakdown
    issue_counts_by_severity: IssuesCountBySeverity
    issue_counts_by_category: IssuesCountByCategory
    issues: List[IssueResponse]
    pages: List[PageResponse]
    forms: List[FormResponse]
    screenshots: List[ScreenshotResponse]
    ai_analysis: Optional[AIAnalysisResponse] = None
    previous_test_run: Optional[TestRunResponse] = None
