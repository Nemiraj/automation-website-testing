import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from .models import Project, Website, ScanResult, TestCase, TestRun, AuthConfig, CrawlConfig

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
os.makedirs(DATA_DIR, exist_ok=True)


class StorageService:
    def __init__(self):
        self.projects: Dict[str, Project] = {}
        self.websites: Dict[str, Website] = {}
        self.scans: Dict[str, ScanResult] = {}
        self.test_cases: Dict[str, List[TestCase]] = {}
        self.test_runs: Dict[str, TestRun] = {}
        self._seed_initial_data()

    def _seed_initial_data(self):
        now = datetime.utcnow().isoformat() + "Z"
        default_proj = Project(
            id="PROJ-DEMO-01",
            name="NovaStore & Cinema Sandbox Platform",
            description="Production sandbox e-commerce and media streaming application with checkout, payment, auth, and catalog flows.",
            createdAt=now,
            updatedAt=now
        )
        self.projects[default_proj.id] = default_proj

        default_web = Website(
            id="WEB-DEMO-01",
            projectId=default_proj.id,
            name="NovaStore Local Sandbox",
            url="http://localhost:3001",
            environment="local",
            authConfig=AuthConfig(
                loginUrl="http://localhost:3001/login",
                testUsername="admin@example.com",
                testPassword="password123"
            ),
            crawlConfig=CrawlConfig(
                maxDepth=3,
                maxPages=10,
                sameOriginOnly=True,
                excludedPaths=[],
                disallowedDestructiveActions=True
            ),
            createdAt=now,
            updatedAt=now
        )
        self.websites[default_web.id] = default_web

    # Projects
    def get_projects(self) -> List[Project]:
        return list(self.projects.values())

    def get_project(self, project_id: str) -> Optional[Project]:
        return self.projects.get(project_id)

    def save_project(self, proj: Project) -> Project:
        self.projects[proj.id] = proj
        return proj

    # Websites
    def get_websites(self, project_id: Optional[str] = None) -> List[Website]:
        all_webs = list(self.websites.values())
        if project_id:
            return [w for w in all_webs if w.projectId == project_id]
        return all_webs

    def get_website(self, website_id: str) -> Optional[Website]:
        return self.websites.get(website_id)

    def save_website(self, web: Website) -> Website:
        self.websites[web.id] = web
        return web

    # Scans
    def get_latest_scan(self, website_id: str) -> Optional[ScanResult]:
        return self.scans.get(website_id)

    def save_scan(self, website_id: str, scan: ScanResult) -> ScanResult:
        self.scans[website_id] = scan
        return scan

    # Test cases
    def get_test_cases(self, website_id: str) -> List[TestCase]:
        return self.test_cases.get(website_id, [])

    def save_test_cases(self, website_id: str, cases: List[TestCase]) -> List[TestCase]:
        self.test_cases[website_id] = cases
        return cases

    # Test runs
    def get_test_runs(self, website_id: Optional[str] = None) -> List[TestRun]:
        runs = sorted(self.test_runs.values(), key=lambda r: r.startedAt, reverse=True)
        if website_id:
            return [r for r in runs if r.websiteId == website_id]
        return runs

    def get_test_run(self, run_id: str) -> Optional[TestRun]:
        return self.test_runs.get(run_id)

    def save_test_run(self, run: TestRun) -> TestRun:
        self.test_runs[run.id] = run
        return run


storage = StorageService()
