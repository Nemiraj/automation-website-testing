import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.app.api.deps import get_db_session
from backend.app.database.session import AsyncSessionLocal
from backend.app.models.test_run import TestRun
from backend.app.models.page import Page
from backend.app.models.issue import Issue
from backend.app.models.form import Form
from backend.app.models.screenshot import Screenshot
from backend.app.models.ai_analysis import AIAnalysis
from backend.app.schemas.test_run import TestRunCreate, TestRunResponse, TestRunStatusResponse
from backend.app.schemas.report import TestReportResponse, ScoreBreakdown, IssuesCountBySeverity, IssuesCountByCategory
from backend.app.schemas.issue import IssueResponse
from backend.app.schemas.page import PageResponse
from backend.app.schemas.form import FormResponse
from backend.app.schemas.screenshot import ScreenshotResponse
from backend.app.schemas.ai_analysis import AIAnalysisResponse
from backend.app.core.security import validate_target_url
from backend.app.services.progress_tracker import progress_tracker
from backend.app.services.test_executor import test_pipeline_executor
from backend.app.core.logging import logger

router = APIRouter()


import threading

def _run_test_in_thread(test_id: str):
    import sys
    if sys.platform == "win32":
        loop = asyncio.WindowsProactorEventLoopPolicy().new_event_loop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def _async_task():
        async with AsyncSessionLocal() as session:
            try:
                await test_pipeline_executor.execute_test(test_id, session)
            except Exception as e:
                logger.error(f"Background execution failed: {e}")

    try:
        loop.run_until_complete(_async_task())
    finally:
        loop.close()


@router.post("", response_model=TestRunStatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_test_run(
    payload: TestRunCreate,
    db: AsyncSession = Depends(get_db_session)
):
    target_type = payload.target_type or "live"
    # Validate target URL for SSRF / protocol safety / localhost mode
    is_valid, msg_or_url = validate_target_url(payload.target_url, target_type=target_type)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg_or_url)

    test_run = TestRun(
        project_id=payload.project_id,
        target_url=msg_or_url,
        target_type=target_type,
        status="pending",
        current_stage="Queued",
        progress_percentage=0,
        config=payload.config.model_dump() if payload.config else {},
        environment={}
    )
    db.add(test_run)
    await db.commit()
    await db.refresh(test_run)

    # Spawn background worker thread with dedicated Proactor loop
    thread = threading.Thread(target=_run_test_in_thread, args=(test_run.id,), daemon=True)
    thread.start()

    return TestRunStatusResponse(
        id=test_run.id,
        target_url=test_run.target_url,
        target_type=test_run.target_type,
        status=test_run.status,
        progress_percentage=test_run.progress_percentage,
        current_stage=test_run.current_stage,
        current_page_url=test_run.current_page_url,
        error_message=test_run.error_message,
        environment=test_run.environment or {},
        created_at=test_run.created_at,
        started_at=test_run.started_at,
        completed_at=test_run.completed_at
    )


@router.get("", response_model=List[TestRunResponse])
async def list_test_runs(
    project_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session)
):
    stmt = select(TestRun).order_by(desc(TestRun.created_at)).limit(limit)
    if project_id:
        stmt = stmt.where(TestRun.project_id == project_id)
        
    result = await db.execute(stmt)
    runs = result.scalars().all()

    return [TestRunResponse.model_validate(r) for r in runs]


@router.get("/{test_id}", response_model=TestRunResponse)
async def get_test_run(test_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = select(TestRun).where(TestRun.id == test_id)
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test run not found")

    return TestRunResponse.model_validate(run)


@router.get("/{test_id}/status", response_model=TestRunStatusResponse)
async def get_test_status(test_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = select(TestRun).where(TestRun.id == test_id)
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test run not found")

    # Check in-memory live progress tracker first
    live_state = progress_tracker.get_latest_state(test_id)
    if live_state:
        return TestRunStatusResponse(
            id=test_id,
            target_url=live_state.get("current_page_url") or run.target_url,
            target_type=run.target_type,
            status=live_state.get("status", run.status),
            progress_percentage=live_state.get("progress_percentage", run.progress_percentage),
            current_stage=live_state.get("current_stage", run.current_stage),
            current_page_url=live_state.get("current_page_url"),
            error_message=live_state.get("error_message"),
            environment=run.environment or {},
            created_at=run.created_at,
            started_at=run.started_at,
            completed_at=run.completed_at
        )

    return TestRunStatusResponse(
        id=run.id,
        target_url=run.target_url,
        target_type=run.target_type,
        status=run.status,
        progress_percentage=run.progress_percentage,
        current_stage=run.current_stage,
        current_page_url=run.current_page_url,
        error_message=run.error_message,
        environment=run.environment or {},
        created_at=run.created_at,
        started_at=run.started_at,
        completed_at=run.completed_at
    )


@router.get("/{test_id}/stream")
async def stream_test_progress(test_id: str):
    """Server-Sent Events stream for real-time progress updates."""
    return StreamingResponse(
        progress_tracker.stream_progress(test_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/{test_id}/report", response_model=TestReportResponse)
async def get_test_report(test_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = (
        select(TestRun)
        .where(TestRun.id == test_id)
        .options(
            selectinload(TestRun.pages),
            selectinload(TestRun.issues),
            selectinload(TestRun.forms),
            selectinload(TestRun.screenshots),
            selectinload(TestRun.ai_analysis)
        )
    )
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test run not found")

    # Group counts
    issues = run.issues or []
    sev_counts = IssuesCountBySeverity(
        critical=sum(1 for i in issues if i.severity.lower() == "critical"),
        high=sum(1 for i in issues if i.severity.lower() == "high"),
        medium=sum(1 for i in issues if i.severity.lower() == "medium"),
        low=sum(1 for i in issues if i.severity.lower() == "low"),
        info=sum(1 for i in issues if i.severity.lower() == "info"),
        total=len(issues)
    )

    cat_counts = IssuesCountByCategory(
        ui=sum(1 for i in issues if i.category.lower() == "ui"),
        responsive=sum(1 for i in issues if i.category.lower() == "responsive"),
        functional=sum(1 for i in issues if i.category.lower() == "functional"),
        forms=sum(1 for i in issues if i.category.lower() == "forms"),
        accessibility=sum(1 for i in issues if i.category.lower() == "accessibility"),
        performance=sum(1 for i in issues if i.category.lower() == "performance"),
        javascript=sum(1 for i in issues if i.category.lower() == "javascript"),
        network=sum(1 for i in issues if i.category.lower() == "network"),
        visual_regression=sum(1 for i in issues if i.category.lower() == "visual_regression")
    )

    scores = ScoreBreakdown(
        overall=run.overall_score or 100.0,
        ui=run.ui_score or 100.0,
        responsive=run.responsive_score or 100.0,
        functional=run.functional_score or 100.0,
        forms=run.forms_score or 100.0,
        accessibility=run.accessibility_score or 100.0,
        performance=run.performance_score or 100.0
    )

    # Previous test run for comparison
    prev_run = None
    if run.project_id:
        p_stmt = select(TestRun).where(
            TestRun.project_id == run.project_id,
            TestRun.id != run.id,
            TestRun.status == "completed"
        ).order_by(desc(TestRun.created_at))
        p_res = await db.execute(p_stmt)
        p_obj = p_res.scalars().first()
        if p_obj:
            prev_run = TestRunResponse.model_validate(p_obj)

    ai_resp = None
    if run.ai_analysis:
        ai_resp = AIAnalysisResponse.model_validate(run.ai_analysis)

    return TestReportResponse(
        test_run=TestRunResponse.model_validate(run),
        scores=scores,
        issue_counts_by_severity=sev_counts,
        issue_counts_by_category=cat_counts,
        issues=[IssueResponse.model_validate(i) for i in issues],
        pages=[PageResponse.model_validate(p) for p in (run.pages or [])],
        forms=[FormResponse.model_validate(f) for f in (run.forms or [])],
        screenshots=[ScreenshotResponse.model_validate(s) for s in (run.screenshots or [])],
        ai_analysis=ai_resp,
        previous_test_run=prev_run
    )


@router.get("/{test_id}/issues", response_model=List[IssueResponse])
async def list_test_issues(
    test_id: str,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    page_url: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    stmt = select(Issue).where(Issue.test_run_id == test_id)
    if category:
        stmt = stmt.where(Issue.category.ilike(category))
    if severity:
        stmt = stmt.where(Issue.severity.ilike(severity))
    if page_url:
        stmt = stmt.where(Issue.page_url == page_url)
        
    result = await db.execute(stmt)
    issues = result.scalars().all()
    return [IssueResponse.model_validate(i) for i in issues]


@router.get("/{test_id}/screenshots", response_model=List[ScreenshotResponse])
async def list_test_screenshots(test_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = select(Screenshot).where(Screenshot.test_run_id == test_id)
    result = await db.execute(stmt)
    screenshots = result.scalars().all()
    return [ScreenshotResponse.model_validate(s) for s in screenshots]
