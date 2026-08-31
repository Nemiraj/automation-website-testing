import os
import sys
import time
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .models import (
    Project,
    Website,
    ScanResult,
    TestCase,
    TestRun,
    PageInfo,
    SiteMapNode,
    RegressionSummary
)
from .storage import storage
from .crawler import WebsiteCrawler
from .test_generator import TestGenerator
from .runner import PlaywrightTestRunner
from .ai.regression_analyzer import compare_test_runs
from .reporting.html_generator import HtmlReportGenerator
from .reporting.json_generator import JsonReportGenerator

# Setup paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.dirname(BACKEND_DIR)
ROOT_DIR = os.path.dirname(API_DIR)
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "public", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

app = FastAPI(
    title="WebTest AI — Python API Engine",
    description="Autonomous Website Testing, Playwright Execution, and Business Impact Diagnostics Engine",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount artifacts folder
app.mount("/artifacts", StaticFiles(directory=ARTIFACTS_DIR), name="artifacts")

# Active execution progress dictionary for SSE
active_runs_map: Dict[str, Dict[str, Any]] = {}


# Request Models
class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = ""


class CreateWebsiteRequest(BaseModel):
    projectId: Optional[str] = "PROJ-DEMO-01"
    name: Optional[str] = None
    url: str
    environment: Optional[str] = "local"


class ScanWebsiteRequest(BaseModel):
    maxDepth: Optional[int] = 3
    maxPages: Optional[int] = 12


class RunTestsRequest(BaseModel):
    browserType: Optional[str] = "chromium"


# 1. Projects API
@app.get("/api/projects", response_model=List[Project])
async def get_projects():
    return storage.get_projects()


@app.post("/api/projects", status_code=201, response_model=Project)
async def create_project(req: CreateProjectRequest):
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Project name is required")
    now = datetime.utcnow().isoformat() + "Z"
    new_proj = Project(
        id=f"PROJ-{int(time.time()*1000)}",
        name=req.name,
        description=req.description or "",
        createdAt=now,
        updatedAt=now
    )
    storage.save_project(new_proj)
    return new_proj


@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    proj = storage.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj


# 2. Websites API
@app.get("/api/websites", response_model=List[Website])
async def get_websites(projectId: Optional[str] = None):
    return storage.get_websites(projectId)


@app.post("/api/websites", status_code=201, response_model=Website)
async def create_website(req: CreateWebsiteRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="Website URL is required")
    now = datetime.utcnow().isoformat() + "Z"
    domain_name = urlparse(req.url).hostname or req.url
    new_website = Website(
        id=f"WEB-{int(time.time()*1000)}",
        projectId=req.projectId or "PROJ-DEMO-01",
        name=req.name or domain_name,
        url=req.url.rstrip("/"),
        environment=req.environment if req.environment in ('local', 'staging', 'production') else 'local',
        createdAt=now,
        updatedAt=now
    )
    storage.save_website(new_website)
    return new_website


@app.get("/api/websites/{website_id}", response_model=Website)
async def get_website(website_id: str):
    web = storage.get_website(website_id)
    if not web:
        raise HTTPException(status_code=404, detail="Website not found")
    return web


# 3. Crawler & Scan API
@app.post("/api/websites/{website_id}/scan")
async def scan_website(website_id: str, req: ScanWebsiteRequest = ScanWebsiteRequest()):
    web = storage.get_website(website_id)
    if not web:
        raise HTTPException(status_code=404, detail="Website not found")

    crawler = WebsiteCrawler(
        root_url=web.url,
        website_id=web.id,
        max_depth=req.maxDepth or 3,
        max_pages=req.maxPages or 12,
        headless=True
    )

    try:
        scan_result = await crawler.scan()
        storage.save_scan(web.id, scan_result)

        # Auto generate test cases from scan
        generated_tests = TestGenerator.generate_tests(web, scan_result)
        storage.save_test_cases(web.id, generated_tests)

        return {
            "success": True,
            "scanResult": scan_result,
            "generatedTestsCount": len(generated_tests),
            "tests": generated_tests
        }
    except Exception as err:
        print(f"[API] Scan execution failed: {err}")
        raise HTTPException(status_code=500, detail=f"Website crawl failed: {str(err)}")


@app.get("/api/websites/{website_id}/scan", response_model=ScanResult)
async def get_latest_scan(website_id: str):
    scan = storage.get_latest_scan(website_id)
    if not scan:
        raise HTTPException(status_code=404, detail="No scan results found for website")
    return scan


# 4. Test Generation API
@app.post("/api/websites/{website_id}/generate-tests")
async def generate_tests_for_website(website_id: str):
    web = storage.get_website(website_id)
    if not web:
        raise HTTPException(status_code=404, detail="Website not found")

    scan = storage.get_latest_scan(web.id)
    if not scan:
        now = datetime.utcnow().isoformat() + "Z"
        scan = ScanResult(
            websiteId=web.id,
            rootUrl=web.url,
            scannedAt=now,
            totalPages=1,
            totalLinks=4,
            totalButtons=2,
            totalForms=1,
            totalInputs=2,
            pages=[
                PageInfo(
                    id='PAGE-ROOT',
                    url=web.url,
                    path='/',
                    title='Home',
                    statusCode=200,
                    loadTimeMs=300,
                    depth=0,
                    internalLinks=[f"{web.url}/products", f"{web.url}/cart", f"{web.url}/checkout", f"{web.url}/login"],
                    externalLinks=[],
                    elements=[],
                    formsCount=1,
                    buttonsCount=2,
                    inputsCount=2,
                    consoleErrorsCount=0,
                    networkErrorsCount=0,
                    healthStatus='HEALTHY',
                    lastScannedAt=now
                )
            ],
            siteMapTree=SiteMapNode(url=web.url, path='/', title='Home', status='HEALTHY', children=[])
        )
        storage.save_scan(web.id, scan)

    generated_tests = TestGenerator.generate_tests(web, scan)
    storage.save_test_cases(web.id, generated_tests)
    return {"count": len(generated_tests), "tests": generated_tests}


@app.get("/api/websites/{website_id}/tests", response_model=List[TestCase])
async def get_test_cases(website_id: str):
    return storage.get_test_cases(website_id)


# 5. Test Execution API
@app.post("/api/websites/{website_id}/test")
async def execute_tests(website_id: str, req: RunTestsRequest = RunTestsRequest()):
    web = storage.get_website(website_id)
    if not web:
        raise HTTPException(status_code=404, detail="Website not found")

    test_cases = storage.get_test_cases(web.id)
    if not test_cases:
        scan = storage.get_latest_scan(web.id)
        if not scan:
            now = datetime.utcnow().isoformat() + "Z"
            scan = ScanResult(
                websiteId=web.id,
                rootUrl=web.url,
                scannedAt=now,
                totalPages=1,
                totalLinks=4,
                totalButtons=2,
                totalForms=1,
                totalInputs=2,
                pages=[
                    PageInfo(
                        id='PAGE-ROOT',
                        url=web.url,
                        path='/',
                        title='Home',
                        statusCode=200,
                        loadTimeMs=300,
                        depth=0,
                        internalLinks=[f"{web.url}/products", f"{web.url}/cart", f"{web.url}/checkout", f"{web.url}/login"],
                        externalLinks=[],
                        elements=[],
                        formsCount=1,
                        buttonsCount=2,
                        inputsCount=2,
                        healthStatus='HEALTHY',
                        lastScannedAt=now
                    )
                ],
                siteMapTree=SiteMapNode(url=web.url, path='/', title='Home', status='HEALTHY', children=[])
            )
            storage.save_scan(web.id, scan)
        test_cases = TestGenerator.generate_tests(web, scan)
        storage.save_test_cases(web.id, test_cases)

    run_id = f"RUN-{int(time.time()*1000)}"
    existing_runs = storage.get_test_runs(web.id)
    previous_run = existing_runs[0] if existing_runs else None

    def on_progress(p: Dict[str, Any]):
        active_runs_map[run_id] = p

    runner = PlaywrightTestRunner(
        run_id=run_id,
        website=web,
        test_cases=test_cases,
        browser_type=req.browserType or 'chromium',
        artifacts_dir=ARTIFACTS_DIR,
        headless=True,
        on_progress=on_progress
    )

    try:
        test_run = await runner.run()

        # Compare regressions
        regressions = compare_test_runs(test_run, previous_run)
        if regressions:
            test_run.regressionSummary = RegressionSummary(
                newFailures=regressions['summary']['newFailuresCount'],
                fixedFailures=regressions['summary']['fixedFailuresCount'],
                continuingFailures=regressions['summary']['continuingFailuresCount'],
                newWarnings=regressions['summary']['newWarningsCount'],
                previousRunId=regressions['previousRunId'],
                previousHealthScore=regressions['previousHealthScore']
            )

        storage.save_test_run(test_run)
        active_runs_map.pop(run_id, None)

        return {
            "success": True,
            "runId": test_run.id,
            "healthScore": test_run.healthScore,
            "totalTests": test_run.totalTests,
            "passedTests": test_run.passedTests,
            "failedTests": test_run.failedTests,
            "criticalFailures": test_run.criticalFailures,
            "testRun": test_run
        }
    except Exception as err:
        active_runs_map.pop(run_id, None)
        print(f"[API] Execution error: {err}")
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(err)}")


# 6. Test Runs & Results API
@app.get("/api/test-runs", response_model=List[TestRun])
async def get_test_runs(websiteId: Optional[str] = None):
    return storage.get_test_runs(websiteId)


@app.get("/api/test-runs/{run_id}", response_model=TestRun)
async def get_test_run(run_id: str):
    run = storage.get_test_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    return run


@app.get("/api/test-runs/{run_id}/compare/{prev_id}")
async def compare_runs_endpoint(run_id: str, prev_id: str):
    current = storage.get_test_run(run_id)
    prev = storage.get_test_run(prev_id)
    if not current or not prev:
        raise HTTPException(status_code=404, detail="One or both test runs not found")
    return compare_test_runs(current, prev)


# 7. Live SSE Progress Stream
@app.get("/api/test-runs/{run_id}/stream")
async def stream_test_progress(run_id: str):
    async def event_generator():
        while True:
            progress = active_runs_map.get(run_id)
            if progress:
                yield f"data: {json.dumps(progress)}\n\n"
            else:
                finished_run = storage.get_test_run(run_id)
                if finished_run:
                    yield f"data: {json.dumps({'status': 'completed', 'testRun': finished_run.model_dump()})}\n\n"
                    break
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# 8. Reports API (HTML & JSON)
@app.get("/api/reports/{run_id}")
async def get_report(run_id: str, format: Optional[str] = "html", download: Optional[bool] = False):
    run = storage.get_test_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")

    if format == "json":
        json_data = JsonReportGenerator.generate(run)
        return Response(
            content=json_data,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="qa-report-{run.id}.json"'}
        )

    html_content = HtmlReportGenerator.generate(run)
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="qa-report-{run.id}.html"'
    return HTMLResponse(content=html_content, headers=headers)


# 9. Health & Observability API
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "engine": "Python FastAPI Playwright Engine",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "activeWorkers": len(active_runs_map),
        "totalProjects": len(storage.get_projects()),
        "totalWebsites": len(storage.get_websites()),
        "totalRunsRecorded": len(storage.get_test_runs())
    }


def main():
    import uvicorn
    port = int(os.environ.get("PORT", 4000))
    print(f"🚀 [WebTestAI Python Engine] Starting FastAPI server on http://localhost:{port}")
    uvicorn.run("apps.api.backend.main:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
