from backend.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from backend.app.schemas.test_run import TestConfig, TestRunCreate, TestRunResponse, TestRunStatusResponse
from backend.app.schemas.page import PageResponse
from backend.app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse
from backend.app.schemas.form import FormResponse
from backend.app.schemas.screenshot import ScreenshotResponse
from backend.app.schemas.ai_analysis import AIAnalysisResponse
from backend.app.schemas.report import TestReportResponse, ScoreBreakdown

__all__ = [
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "TestConfig",
    "TestRunCreate",
    "TestRunResponse",
    "TestRunStatusResponse",
    "PageResponse",
    "IssueCreate",
    "IssueUpdate",
    "IssueResponse",
    "FormResponse",
    "ScreenshotResponse",
    "AIAnalysisResponse",
    "TestReportResponse",
    "ScoreBreakdown",
]
