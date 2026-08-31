import os
import sys
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

# Ensure backend directory and root directory are in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from backend.models import (
        Project,
        Website,
        ScanResult,
        TestCase,
        TestRun,
        BrowserType,
        EnvironmentType
    )
    from backend.storage import storage
    from backend.crawler import WebsiteCrawler
    from backend.test_generator import TestGenerator
    from backend.runner import PlaywrightTestRunner
    from backend.ai.regression_analyzer import compare_test_runs
    from backend.reporting.html_generator import HtmlReportGenerator
    from backend.reporting.json_generator import JsonReportGenerator
except ImportError:
    from models import (
        Project,
        Website,
        ScanResult,
        TestCase,
        TestRun,
        BrowserType,
        EnvironmentType
    )
    from storage import storage
    from crawler import WebsiteCrawler
    from test_generator import TestGenerator
    from runner import PlaywrightTestRunner
    from ai.regression_analyzer import compare_test_runs
    from reporting.html_generator import HtmlReportGenerator
    from reporting.json_generator import JsonReportGenerator

from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ARTIFACTS_DIR = os.path.join(ROOT_DIR, "public", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

app = FastAPI(
    title="WebTest AI Python Backend",
    description="Python FastAPI engine for autonomous web crawling, test synthesis, Playwright execution, and AI failure diagnostics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/artifacts", StaticFiles(directory=ARTIFACTS_DIR), name="artifacts")

live_progress_streams: Dict[str, asyncio.Queue] = {}


# Request Models
class ScanWebsiteRequest(BaseModel):
    url: Optional[str] = None
    maxPages: Optional[int] = 10
    maxDepth: Optional[int] = 3


class RunTestsRequest(BaseModel):
    url: Optional[str] = None
    browserType: Optional[BrowserType] = "chromium"


class CreateProjectRequest(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = ""


class CreateWebsiteRequest(BaseModel):
    id: Optional[str] = None
    projectId: str
    name: str
    url: str
    environment: Optional[EnvironmentType] = "local"
    authConfig: Optional[Dict[str, Any]] = None
    crawlConfig: Optional[Dict[str, Any]] = None


# 1. Projects
@app.get("/api/projects", response_model=List[Project])
async def get_projects():
    return storage.get_projects()


@app.post("/api/projects", response_model=Project)
async def create_project(req: CreateProjectRequest):
    # id is generated server-side if the caller doesn't supply one, so clients
    # can POST just {"name": "..."} instead of being forced to invent an id.
    proj = Project(
        id=req.id or f"PROJ-{uuid.uuid4().hex[:8].upper()}",
        name=req.name,
        description=req.description or ""
    )
    return storage.save_project(proj)


@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    p = storage.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


# 2. Websites
@app.get("/api/websites", response_model=List[Website])
async def get_websites(projectId: Optional[str] = None):
    return storage.get_websites(projectId)


@app.post("/api/websites", response_model=Website)
async def create_website(req: CreateWebsiteRequest):
    web = Website(
        id=req.id or f"WEB-{uuid.uuid4().hex[:8].upper()}",
        projectId=req.projectId,
        name=req.name,
        url=req.url,
        environment=req.environment or "local",
        authConfig=req.authConfig,
        crawlConfig=req.crawlConfig
    )
    return storage.save_website(web)


@app.get("/api/websites/{website_id}", response_model=Website)
async def get_website(website_id: str):
    w = storage.get_website(website_id)
    if not w:
        raise HTTPException(status_code=404, detail="Website not found")
    return w


# 3. Scanning & Discovery
@app.post("/api/websites/{website_id}/scan")
async def scan_website(website_id: str, req: ScanWebsiteRequest = ScanWebsiteRequest()):
    website = storage.get_website(website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    target_url = (req.url or website.url).rstrip('/')
    website.url = target_url
    storage.save_website(website)

    crawler = WebsiteCrawler(
        root_url=target_url,
        website_id=website.id,
        max_depth=req.maxDepth or 3,
        max_pages=req.maxPages or 10,
        same_origin_only=True,
        headless=True
    )

    scan_result = await crawler.scan()
    storage.save_scan(website_id, scan_result)

    tests = TestGenerator.generate_tests(website, scan_result)
    storage.save_test_cases(website_id, tests)

    return {
        "success": True,
        "scanResult": scan_result,
        "tests": tests,
        "totalPages": scan_result.totalPages,
        "totalLinks": scan_result.totalLinks
    }


@app.get("/api/websites/{website_id}/scan", response_model=ScanResult)
async def get_website_scan(website_id: str):
    scan = storage.get_latest_scan(website_id)
    if not scan:
        website = storage.get_website(website_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        crawler = WebsiteCrawler(root_url=website.url, website_id=website.id)
        scan = await crawler.scan()
        storage.save_scan(website_id, scan)
    return scan


# 4. Test Synthesis & Cases
@app.post("/api/websites/{website_id}/generate-tests", response_model=List[TestCase])
async def generate_tests(website_id: str):
    website = storage.get_website(website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    scan = storage.get_latest_scan(website_id)
    if not scan:
        crawler = WebsiteCrawler(root_url=website.url, website_id=website.id)
        scan = await crawler.scan()
        storage.save_scan(website_id, scan)

    tests = TestGenerator.generate_tests(website, scan)
    storage.save_test_cases(website_id, tests)
    return tests


@app.get("/api/websites/{website_id}/tests", response_model=List[TestCase])
async def get_tests(website_id: str):
    tests = storage.get_test_cases(website_id)
    if not tests:
        website = storage.get_website(website_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        scan = storage.get_latest_scan(website_id)
        if not scan:
            crawler = WebsiteCrawler(root_url=website.url, website_id=website.id)
            scan = await crawler.scan()
            storage.save_scan(website_id, scan)
        tests = TestGenerator.generate_tests(website, scan)
        storage.save_test_cases(website_id, tests)
    return tests


# 5. Test Execution
@app.post("/api/websites/{website_id}/test")
async def execute_tests(website_id: str, req: RunTestsRequest = RunTestsRequest()):
    website = storage.get_website(website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    url_changed = False
    if req.url and req.url.rstrip('/') != website.url:
        website.url = req.url.rstrip('/')
        storage.save_website(website)
        url_changed = True

    tests = storage.get_test_cases(website_id)
    if not tests or url_changed:
        crawler = WebsiteCrawler(root_url=website.url, website_id=website.id)
        scan = await crawler.scan()
        storage.save_scan(website_id, scan)
        tests = TestGenerator.generate_tests(website, scan)
        storage.save_test_cases(website_id, tests)

    run_id = f"RUN-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    progress_queue: asyncio.Queue = asyncio.Queue()
    live_progress_streams[run_id] = progress_queue

    def on_progress(p_data: Dict[str, Any]):
        try:
            progress_queue.put_nowait(p_data)
        except Exception:
            pass

    runner = PlaywrightTestRunner(
        run_id=run_id,
        website=website,
        test_cases=tests,
        browser_type=req.browserType or "chromium",
        artifacts_dir=ARTIFACTS_DIR,
        headless=True,
        on_progress=on_progress
    )

    test_run = await runner.run()

    # Compare with previous run for regression analysis
    runs_history = storage.get_test_runs(website_id)
    if runs_history:
        prev_run = runs_history[0]
        regression = compare_test_runs(test_run, prev_run)
        if regression:
            try:
                from backend.models import RegressionSummary
            except ImportError:
                from models import RegressionSummary
            test_run.regressionSummary = RegressionSummary(
                newFailures=len(regression['newFailures']),
                fixedFailures=len(regression['fixedFailures']),
                continuingFailures=len(regression['continuingFailures']),
                newWarnings=len(regression['newWarnings']),
                previousRunId=prev_run.id,
                previousHealthScore=prev_run.healthScore
            )

    storage.save_test_run(test_run)
    return {"success": True, "testRun": test_run}


# 6. Test Runs
@app.get("/api/test-runs", response_model=List[TestRun])
async def get_test_runs(websiteId: Optional[str] = None):
    return storage.get_test_runs(websiteId)


@app.get("/api/test-runs/{run_id}", response_model=TestRun)
async def get_test_run(run_id: str):
    r = storage.get_test_run(run_id)
    if not r:
        raise HTTPException(status_code=404, detail="Test run not found")
    return r


@app.get("/api/test-runs/{run_id}/compare/{prev_run_id}")
async def compare_runs(run_id: str, prev_run_id: str):
    curr = storage.get_test_run(run_id)
    prev = storage.get_test_run(prev_run_id)
    if not curr or not prev:
        raise HTTPException(status_code=404, detail="One or both test runs not found")

    comparison = compare_test_runs(curr, prev)
    return {"success": True, "comparison": comparison}


# 7. SSE Live Stream
@app.get("/api/test-runs/{run_id}/stream")
async def stream_test_progress(run_id: str):
    queue = live_progress_streams.get(run_id)
    if not queue:
        queue = asyncio.Queue()
        live_progress_streams[run_id] = queue

    async def event_generator():
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") == "completed" or data.get("completedPercentage") == 100:
                    break
        except asyncio.CancelledError:
            pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# 8. Reports
@app.get("/api/reports/{run_id}")
async def get_report(
    run_id: str,
    format: str = Query("html", pattern="^(html|json)$"),
    download: bool = False
):
    r = storage.get_test_run(run_id)
    if not r:
        raise HTTPException(status_code=404, detail="Test run not found")

    if format == "json":
        json_content = JsonReportGenerator.generate(r)
        headers = {}
        if download:
            headers["Content-Disposition"] = f'attachment; filename="report-{run_id}.json"'
        return Response(content=json_content, media_type="application/json", headers=headers)

    html_content = HtmlReportGenerator.generate(r)
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="report-{run_id}.html"'
    return HTMLResponse(content=html_content, headers=headers)


# 9. Health
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "engine": "Python 3.x FastAPI",
        "playwright": "Active",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)

