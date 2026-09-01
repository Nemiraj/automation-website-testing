import asyncio
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.logging import logger
from backend.app.core.config import settings
from backend.app.models.test_run import TestRun
from backend.app.models.page import Page as PageModel
from backend.app.models.issue import Issue as IssueModel
from backend.app.models.form import Form as FormModel
from backend.app.models.screenshot import Screenshot as ScreenshotModel
from backend.app.models.ai_analysis import AIAnalysis as AIAnalysisModel

from backend.app.services.browser import BrowserSession, PageEventManager
from backend.app.services.crawler import WebsiteCrawler
from backend.app.services.link_analyzer import LinkAnalyzer
from backend.app.services.image_analyzer import ImageAnalyzer
from backend.app.services.network_monitor import NetworkAndJSAnalyzer
from backend.app.services.ui_analyzer import UIAnalyzer
from backend.app.services.responsive_analyzer import ResponsiveAnalyzer
from backend.app.services.form_analyzer import FormAnalyzer
from backend.app.services.accessibility_analyzer import AccessibilityAnalyzer
from backend.app.services.performance_analyzer import PerformanceAnalyzer
from backend.app.services.visual_regression import VisualRegressionAnalyzer
from backend.app.services.scoring import calculate_test_scores
from backend.app.services.ai_analyzer import AIAnalyzer
from backend.app.services.progress_tracker import progress_tracker


class TestPipelineExecutor:
    def __init__(self):
        self.link_analyzer = LinkAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        self.network_analyzer = NetworkAndJSAnalyzer()
        self.ui_analyzer = UIAnalyzer()
        self.responsive_analyzer = ResponsiveAnalyzer()
        self.form_analyzer = FormAnalyzer()
        self.a11y_analyzer = AccessibilityAnalyzer()
        self.perf_analyzer = PerformanceAnalyzer()
        self.visual_analyzer = VisualRegressionAnalyzer()
        self.ai_analyzer = AIAnalyzer()

    async def execute_test(self, test_id: str, db: AsyncSession):
        logger.info(f"Starting test execution pipeline for test_id: {test_id}")
        
        # 1. Fetch TestRun from DB
        stmt = select(TestRun).where(TestRun.id == test_id)
        result = await db.execute(stmt)
        test_run = result.scalar_one_or_none()

        if not test_run:
            logger.error(f"TestRun with id {test_id} not found.")
            return

        test_run.status = "running"
        test_run.started_at = datetime.utcnow()
        await db.commit()

        target_url = test_run.target_url
        config = test_run.config or {}
        max_pages = config.get("max_pages", 10)
        viewports_to_test = config.get("viewports", ["desktop_large", "tablet", "mobile_large"])
        form_submission_mode = config.get("form_submission_mode", "validation_only")

        progress_tracker.update_progress(test_id, 10, "Connecting to target website", target_url)

        browser_session: Optional[BrowserSession] = None
        all_issues: List[Dict[str, Any]] = []
        all_screenshots: List[Dict[str, Any]] = []
        all_forms: List[Dict[str, Any]] = []
        created_pages: List[PageModel] = []

        try:
            # 2. Launch Chromium browser
            browser_session = await BrowserSession.create()

            # 3. Crawl target website
            progress_tracker.update_progress(test_id, 20, "Crawling website pages", target_url)
            crawler = WebsiteCrawler(base_url=target_url, max_pages=max_pages, timeout_ms=settings.DEFAULT_TIMEOUT_MS)
            crawled_pages = await crawler.crawl(browser_session)
            
            progress_tracker.update_progress(test_id, 35, f"Discovered {len(crawled_pages)} pages. Beginning inspection.")

            # 4. Iterate over crawled pages and perform deterministic test modules
            for idx, p_data in enumerate(crawled_pages):
                current_p_url = p_data.url
                page_percent = 35 + int((idx / max(1, len(crawled_pages))) * 45)
                progress_tracker.update_progress(test_id, page_percent, f"Testing page: {current_p_url}", current_p_url)

                # Create Page DB record
                page_db = PageModel(
                    test_run_id=test_id,
                    url=current_p_url,
                    status_code=p_data.status_code,
                    title=p_data.title,
                    meta_description=p_data.meta_description,
                    canonical_url=p_data.canonical_url,
                    links_count=p_data.links_count,
                    images_count=p_data.images_count,
                    forms_count=p_data.forms_count,
                    buttons_count=p_data.buttons_count,
                    scripts_count=p_data.scripts_count,
                    stylesheets_count=p_data.stylesheets_count,
                    headings=p_data.headings
                )
                db.add(page_db)
                await db.flush()
                created_pages.append(page_db)

                # Open page in browser for rich dynamic evaluations
                context = await browser_session.new_context("desktop_standard")
                try:
                    page = await context.new_page()
                    event_mgr = PageEventManager(page)

                    try:
                        await page.goto(current_p_url, wait_until="domcontentloaded", timeout=settings.DEFAULT_TIMEOUT_MS)
                        try:
                            await page.wait_for_load_state("networkidle", timeout=3000)
                        except Exception:
                            pass

                        # A. Broken Links Analysis
                        if config.get("enable_links", True) and p_data.extracted_internal_links:
                            link_issues = await self.link_analyzer.analyze_page_links(current_p_url, p_data.extracted_internal_links[:20])
                            for li in link_issues:
                                li["page_id"] = page_db.id
                            all_issues.extend(link_issues)

                        # B. Image Diagnostics
                        if config.get("enable_images", True):
                            img_issues = await self.image_analyzer.analyze_images(page, current_p_url)
                            for ii in img_issues:
                                ii["page_id"] = page_db.id
                            all_issues.extend(img_issues)

                        # C. Console Errors & Network Failures
                        if config.get("enable_javascript", True):
                            net_issues = self.network_analyzer.analyze_events(event_mgr, current_p_url)
                            for ni in net_issues:
                                ni["page_id"] = page_db.id
                            all_issues.extend(net_issues)

                        # D. Form Discovery & Safe Validation
                        if config.get("enable_forms", True):
                            forms_data, form_issues = await self.form_analyzer.discover_and_test_forms(page, current_p_url, form_submission_mode)
                            for f in forms_data:
                                form_db = FormModel(
                                    test_run_id=test_id,
                                    page_id=page_db.id,
                                    page_url=current_p_url,
                                    selector=f["selector"],
                                    action=f["action"],
                                    method=f["method"],
                                    fields=f["fields"],
                                    has_submit_button=f["has_submit_button"],
                                    has_validation=f["has_validation"],
                                    validation_results=f["validation_results"]
                                )
                                db.add(form_db)
                                all_forms.append(f)
                            for fi in form_issues:
                                fi["page_id"] = page_db.id
                            all_issues.extend(form_issues)

                        # E. Accessibility Audit
                        if config.get("enable_accessibility", True):
                            a11y_issues = await self.a11y_analyzer.analyze_accessibility(page, current_p_url)
                            for ai in a11y_issues:
                                ai["page_id"] = page_db.id
                            all_issues.extend(a11y_issues)

                        # F. Performance Metrics
                        if config.get("enable_performance", True):
                            perf_metrics, perf_issues = await self.perf_analyzer.analyze_performance(page, current_p_url)
                            page_db.load_time_ms = perf_metrics.get("load_time_ms")
                            page_db.dom_content_loaded_ms = perf_metrics.get("dom_content_loaded_ms")
                            page_db.first_contentful_paint_ms = perf_metrics.get("first_contentful_paint_ms")
                            page_db.transfer_size_bytes = perf_metrics.get("transfer_size_bytes", 0)
                            page_db.raw_metrics = perf_metrics
                            
                            for pi in perf_issues:
                                pi["page_id"] = page_db.id
                            all_issues.extend(perf_issues)

                    except Exception as e:
                        logger.warning(f"Error during page evaluation for {current_p_url}: {e}")
                    finally:
                        await page.close()
                finally:
                    await context.close()

                # G. Multi-viewport Responsive Layout & Screenshots
                if config.get("enable_responsive", True) or config.get("enable_screenshots", True):
                    resp_issues, screenshots_meta = await self.responsive_analyzer.test_page_viewports(
                        browser_session=browser_session,
                        page_url=current_p_url,
                        test_id=test_id,
                        viewports_to_test=viewports_to_test
                    )
                    for ri in resp_issues:
                        ri["page_id"] = page_db.id
                    all_issues.extend(resp_issues)

                    for sm in screenshots_meta:
                        screenshot_db = ScreenshotModel(
                            test_run_id=test_id,
                            page_id=page_db.id,
                            page_url=current_p_url,
                            viewport=sm["viewport"],
                            width=sm["width"],
                            height=sm["height"],
                            file_path=sm["file_path"],
                            url_path=sm["url_path"],
                            is_full_page=sm["is_full_page"]
                        )
                        db.add(screenshot_db)
                        all_screenshots.append(sm)

            # 5. Visual Regression Analysis (if previous test run exists for this project/URL)
            progress_tracker.update_progress(test_id, 85, "Performing visual regression check")
            if test_run.project_id:
                prev_stmt = select(TestRun).where(
                    TestRun.project_id == test_run.project_id,
                    TestRun.id != test_id,
                    TestRun.status == "completed"
                ).order_by(TestRun.created_at.desc())
                prev_res = await db.execute(prev_stmt)
                prev_run = prev_res.scalars().first()
                
                if prev_run:
                    # Fetch prev screenshots
                    prev_s_stmt = select(ScreenshotModel).where(ScreenshotModel.test_run_id == prev_run.id)
                    prev_s_res = await db.execute(prev_s_stmt)
                    prev_screenshots = [{"file_path": s.file_path, "url_path": s.url_path, "page_url": s.page_url, "viewport": s.viewport} for s in prev_s_res.scalars().all()]
                    
                    vis_issues = self.visual_analyzer.compare_test_runs(all_screenshots, prev_screenshots, test_id=test_id)
                    all_issues.extend(vis_issues)

            # 6. Calculate Deterministic Scores
            progress_tracker.update_progress(test_id, 90, "Calculating health scores")
            scores = calculate_test_scores(all_issues)
            test_run.overall_score = scores["overall"]
            test_run.ui_score = scores["ui"]
            test_run.responsive_score = scores["responsive"]
            test_run.functional_score = scores["functional"]
            test_run.forms_score = scores["forms"]
            test_run.accessibility_score = scores["accessibility"]
            test_run.performance_score = scores["performance"]

            # 7. Persist Issues to DB
            for iss in all_issues:
                issue_db = IssueModel(
                    test_run_id=test_id,
                    page_id=iss.get("page_id"),
                    page_url=iss.get("page_url", target_url),
                    category=iss.get("category", "ui"),
                    severity=iss.get("severity", "low"),
                    title=iss.get("title", "Issue"),
                    description=iss.get("description", ""),
                    why_it_matters=iss.get("why_it_matters"),
                    recommendation=iss.get("recommendation"),
                    suggested_fix=iss.get("suggested_fix"),
                    selector=iss.get("selector"),
                    viewport=iss.get("viewport"),
                    evidence=iss.get("evidence", {}),
                    screenshot_url=iss.get("screenshot_url")
                )
                db.add(issue_db)

            # 8. AI Recommendations Analysis
            progress_tracker.update_progress(test_id, 95, "Generating AI diagnoses and recommendations")
            if config.get("enable_ai", True):
                ai_result = await self.ai_analyzer.analyze_test_run(
                    target_url=target_url,
                    issues=all_issues,
                    scores=scores,
                    pages_count=len(created_pages)
                )
                ai_db = AIAnalysisModel(
                    test_run_id=test_id,
                    summary=ai_result.get("summary", ""),
                    issues_analysis=ai_result.get("issues", []),
                    priority_actions=ai_result.get("priority_actions", []),
                    raw_response=ai_result,
                    model_used=ai_result.get("model_used", "AI Engine")
                )
                db.add(ai_db)

            # 9. Update TestRun completion stats
            test_run.status = "completed"
            test_run.completed_at = datetime.utcnow()
            test_run.total_pages_scanned = len(created_pages)
            test_run.critical_issues_count = sum(1 for i in all_issues if i.get("severity") == "critical")
            test_run.high_issues_count = sum(1 for i in all_issues if i.get("severity") == "high")
            test_run.medium_issues_count = sum(1 for i in all_issues if i.get("severity") == "medium")
            test_run.low_issues_count = sum(1 for i in all_issues if i.get("severity") == "low")
            test_run.info_issues_count = sum(1 for i in all_issues if i.get("severity") == "info")
            test_run.progress_percentage = 100
            test_run.current_stage = "Completed"

            await db.commit()
            progress_tracker.update_progress(test_id, 100, "Completed", current_page=None, status="completed")
            logger.info(f"Test run {test_id} successfully completed with score {scores['overall']}")

        except Exception as e:
            logger.error(f"Fatal error executing test {test_id}: {e}\n{traceback.format_exc()}")
            test_run.status = "failed"
            test_run.error_message = str(e)
            test_run.completed_at = datetime.utcnow()
            await db.commit()
            progress_tracker.update_progress(test_id, 100, f"Failed: {str(e)}", error_message=str(e), status="failed")

        finally:
            if browser_session:
                await browser_session.close()


test_pipeline_executor = TestPipelineExecutor()
