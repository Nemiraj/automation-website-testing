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

from backend.app.core.security import resolve_internal_url
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
from backend.app.services.tech_detector import tech_detector
from backend.app.services.server_error_detector import server_error_detector
from backend.app.services.screenshot_annotator import screenshot_annotator
from backend.app.services.source_inspector import source_inspector
from backend.app.services.ai_readiness import ai_readiness_analyzer
from backend.app.services.solution_engine import solution_engine
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
        self.tech_detector = tech_detector
        self.server_error_detector = server_error_detector

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

            # Optional Local Development Login
            auth_login_url = config.get("auth_login_url")
            auth_user = config.get("auth_username")
            auth_pass = config.get("auth_password")
            if auth_login_url and auth_user and auth_pass:
                try:
                    progress_tracker.update_progress(test_id, 15, "Authenticating test session", auth_login_url)
                    auth_context = await browser_session.new_context("desktop_standard")
                    auth_page = await auth_context.new_page()
                    await auth_page.goto(auth_login_url, wait_until="domcontentloaded", timeout=settings.DEFAULT_TIMEOUT_MS)
                    user_input = await auth_page.query_selector("input[type='text'], input[type='email'], input[name*='user'], input[name*='email'], input[id*='user'], input[id*='email']")
                    if user_input:
                        await user_input.fill(auth_user)
                    pass_input = await auth_page.query_selector("input[type='password']")
                    if pass_input:
                        await pass_input.fill(auth_pass)
                    submit_btn = await auth_page.query_selector("button[type='submit'], input[type='submit'], button:not([type='button'])")
                    if submit_btn:
                        await submit_btn.click()
                        try:
                            await auth_page.wait_for_load_state("networkidle", timeout=5000)
                        except Exception:
                            pass
                    await auth_page.close()
                    await auth_context.close()
                except Exception as auth_err:
                    logger.warning(f"Auth login attempt encountered issue: {auth_err}")

            # 3. Crawl target website
            progress_tracker.update_progress(test_id, 20, "Crawling website pages", target_url)
            crawler = WebsiteCrawler(base_url=target_url, max_pages=max_pages, timeout_ms=settings.DEFAULT_TIMEOUT_MS)
            crawled_pages = await crawler.crawl(browser_session)
            
            # Detect server technology and environment
            first_page = crawled_pages[0] if crawled_pages else None
            detected_env = self.tech_detector.detect_technology(
                url=target_url,
                target_type=test_run.target_type,
                headers=first_page.response_headers if first_page else {},
                html_content=first_page.html_content if first_page else "",
                cookies=first_page.cookies if first_page else []
            )
            user_tech = config.get("technology", "auto")
            if user_tech and user_tech.lower() != "auto":
                detected_env["technology"] = user_tech.upper()
                
            test_run.environment = detected_env
            await db.commit()

            progress_tracker.update_progress(test_id, 35, f"Discovered {len(crawled_pages)} pages. Beginning inspection.")

            crawled_pages_data = []

            # 4. Iterate over crawled pages and perform deterministic test modules
            for idx, p_data in enumerate(crawled_pages):
                current_p_url = p_data.url
                page_percent = 35 + int((idx / max(1, len(crawled_pages))) * 45)
                progress_tracker.update_progress(test_id, page_percent, f"Testing page: {current_p_url}", current_p_url)

                crawled_pages_data.append({
                    "url": current_p_url,
                    "html": p_data.html_content,
                    "title": p_data.title,
                    "meta_description": p_data.meta_description
                })

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

                # Server & PHP / Database Error Detection on Rendered HTML
                server_issues = self.server_error_detector.scan_page_content(p_data.html_content, current_p_url)
                for si in server_issues:
                    si["page_id"] = page_db.id
                all_issues.extend(server_issues)

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
            progress_tracker.update_progress(test_id, 88, "Annotating visual issue locations on screenshots")
            scores = calculate_test_scores(all_issues)
            test_run.overall_score = scores["overall"]
            test_run.ui_score = scores["ui"]
            test_run.responsive_score = scores["responsive"]
            test_run.functional_score = scores["functional"]
            test_run.forms_score = scores["forms"]
            test_run.accessibility_score = scores["accessibility"]
            test_run.performance_score = scores["performance"]

            # Map screenshots by (page_url, viewport) and viewport
            screenshot_map = {}
            for sm in all_screenshots:
                key = (sm.get("page_url"), sm.get("viewport"))
                screenshot_map[key] = sm
                if sm.get("viewport"):
                    screenshot_map[sm["viewport"]] = sm

            # Resolve local source directory (explicit or auto-detected for XAMPP)
            local_src_dir = config.get("local_source_dir")
            if not local_src_dir and "localhost" in target_url:
                try:
                    from urllib.parse import urlparse
                    path_parts = [p for p in urlparse(target_url).path.split("/") if p]
                    if path_parts:
                        xampp_candidate = os.path.join(r"C:\xampp\htdocs", path_parts[0])
                        if os.path.exists(xampp_candidate):
                            local_src_dir = xampp_candidate
                except Exception:
                    pass

            # 7. Assign issue numbers, generate visual annotations, map source files & persist to DB
            for idx, iss in enumerate(all_issues, start=1):
                iss["issue_number"] = idx
                vp = iss.get("viewport") or "desktop_standard"
                p_url = iss.get("page_url")
                
                # Match screenshot
                sm = screenshot_map.get((p_url, vp)) or screenshot_map.get(vp) or (all_screenshots[0] if all_screenshots else None)
                if sm:
                    iss["screenshot_url"] = sm.get("url_path")
                    if iss.get("coordinates") and iss["coordinates"].get("width"):
                        vp_w = sm.get("width", 1280)
                        vp_h = sm.get("height", 800)
                        ann_res = screenshot_annotator.annotate_single_issue(
                            screenshot_path=sm["file_path"],
                            issue=iss,
                            viewport_size=(vp_w, vp_h),
                            test_id=test_id
                        )
                        if ann_res:
                            iss["annotated_screenshot_url"] = ann_res["url_path"]

                # Source code inspection & fix confidence
                selector = iss.get("selector")
                source_meta = source_inspector.inspect_selector_source(selector, local_src_dir)
                iss["source_location"] = source_meta

                # Confidence calculation
                if source_meta.get("confidence") == "confirmed":
                    fix_conf = "high"
                elif iss.get("fix_confidence"):
                    fix_conf = iss["fix_confidence"]
                else:
                    fix_conf = "medium" if selector else "low"

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
                    issue_number=iss.get("issue_number"),
                    section=iss.get("section", "General"),
                    selector=selector,
                    viewport=iss.get("viewport"),
                    coordinates=iss.get("coordinates", {}),
                    marker_type=iss.get("marker_type", "rectangle"),
                    source_location=source_meta,
                    fix_confidence=fix_conf,
                    fix_reasoning=iss.get("fix_reasoning") or f"Directly determined from {selector or 'rendered DOM'} layout and computed metrics.",
                    evidence=iss.get("evidence", {}),
                    screenshot_url=iss.get("screenshot_url"),
                    annotated_screenshot_url=iss.get("annotated_screenshot_url")
                )
                db.add(issue_db)

            # Generate combined multi-issue annotated screenshots for viewports
            for sm in all_screenshots:
                vp = sm.get("viewport", "desktop_standard")
                vp_issues = [i for i in all_issues if (i.get("viewport") == vp or not i.get("viewport")) and i.get("coordinates")]
                if vp_issues:
                    multi_ann = screenshot_annotator.annotate_multi_issues(
                        screenshot_path=sm["file_path"],
                        issues=vp_issues,
                        viewport_size=(sm.get("width", 1280), sm.get("height", 800)),
                        test_id=test_id,
                        viewport_name=vp
                    )
                    if multi_ann:
                        sm["annotated_url_path"] = multi_ann["url_path"]

            # 8. AI Readiness Checker
            progress_tracker.update_progress(test_id, 92, "Running deterministic AI Readiness audit")
            ai_readiness_res = ai_readiness_analyzer.analyze_readiness(
                pages_data=crawled_pages_data,
                all_issues=all_issues,
                is_localhost=("localhost" in target_url or test_run.target_type == "localhost")
            )
            test_run.ai_readiness_score = ai_readiness_res.get("overall_score")
            test_run.ai_readiness_data = ai_readiness_res

            # 9. Report-Based Solution Engine
            progress_tracker.update_progress(test_id, 95, "Generating prioritized developer solution plan")
            solution_plan_res = solution_engine.generate_solution_plan(
                test_id=test_id,
                target_url=target_url,
                all_issues=all_issues,
                ai_readiness_data=ai_readiness_res,
                local_source_dir=local_src_dir
            )
            test_run.solution_plan = solution_plan_res

            # 10. AI Recommendations Analysis (Optional LLM synthesis)
            if config.get("enable_ai", True):
                ai_result = await self.ai_analyzer.analyze_test_run(
                    target_url=target_url,
                    issues=all_issues,
                    scores=scores,
                    pages_count=len(created_pages),
                    target_type=test_run.target_type,
                    environment=test_run.environment
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

            # 11. Update TestRun completion stats
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
            logger.info(f"Test run {test_id} successfully completed with score {scores['overall']}, AI readiness {test_run.ai_readiness_score}")

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
