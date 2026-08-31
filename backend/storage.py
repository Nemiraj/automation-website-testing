import os
import sys
import json
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from backend.models import Project, Website, ScanResult, TestCase, TestRun, AuthConfig, CrawlConfig
except ImportError:
    from models import Project, Website, ScanResult, TestCase, TestRun, AuthConfig, CrawlConfig

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Every collection is persisted as one JSON file containing a list/dict of the
# model's serialized data. This is intentionally simple (no real DB) but means
# projects/websites/scans/tests/runs now survive a server restart instead of
# vanishing the moment the process stops, which was silently the case before
# even though a "data/" directory was already being created for this purpose.
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
WEBSITES_FILE = os.path.join(DATA_DIR, "websites.json")
SCANS_FILE = os.path.join(DATA_DIR, "scans.json")
TEST_CASES_FILE = os.path.join(DATA_DIR, "test_cases.json")
TEST_RUNS_FILE = os.path.join(DATA_DIR, "test_runs.json")


def _atomic_write(path: str, data: Any) -> None:
    """Write JSON to a temp file then rename, so a crash mid-write can't corrupt the file."""
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp_path, path)


def _load_json(path: str) -> Optional[Any]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Storage] Warning: could not read {path} ({e}). Starting fresh for this collection.")
        return None


class StorageService:
    def __init__(self):
        self._lock = threading.Lock()
        self.projects: Dict[str, Project] = {}
        self.websites: Dict[str, Website] = {}
        self.scans: Dict[str, ScanResult] = {}
        self.test_cases: Dict[str, List[TestCase]] = {}
        self.test_runs: Dict[str, TestRun] = {}

        if not self._load_from_disk():
            # Nothing persisted yet (fresh install) — seed the demo project/website
            # so the app isn't empty on first run.
            self._seed_initial_data()
            self._persist_all()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load_from_disk(self) -> bool:
        """Returns True if any persisted data was found and loaded."""
        found_any = False

        raw_projects = _load_json(PROJECTS_FILE)
        if raw_projects is not None:
            found_any = True
            for p in raw_projects:
                proj = Project(**p)
                self.projects[proj.id] = proj

        raw_websites = _load_json(WEBSITES_FILE)
        if raw_websites is not None:
            found_any = True
            for w in raw_websites:
                web = Website(**w)
                self.websites[web.id] = web

        raw_scans = _load_json(SCANS_FILE)
        if raw_scans is not None:
            found_any = True
            for website_id, scan_dict in raw_scans.items():
                self.scans[website_id] = ScanResult(**scan_dict)

        raw_test_cases = _load_json(TEST_CASES_FILE)
        if raw_test_cases is not None:
            found_any = True
            for website_id, cases in raw_test_cases.items():
                self.test_cases[website_id] = [TestCase(**c) for c in cases]

        raw_test_runs = _load_json(TEST_RUNS_FILE)
        if raw_test_runs is not None:
            found_any = True
            for run_id, run_dict in raw_test_runs.items():
                self.test_runs[run_id] = TestRun(**run_dict)

        return found_any

    def _persist_all(self) -> None:
        with self._lock:
            _atomic_write(PROJECTS_FILE, [p.model_dump(mode="json") for p in self.projects.values()])
            _atomic_write(WEBSITES_FILE, [w.model_dump(mode="json") for w in self.websites.values()])
            _atomic_write(SCANS_FILE, {k: v.model_dump(mode="json") for k, v in self.scans.items()})
            _atomic_write(TEST_CASES_FILE, {k: [c.model_dump(mode="json") for c in v] for k, v in self.test_cases.items()})
            _atomic_write(TEST_RUNS_FILE, {k: v.model_dump(mode="json") for k, v in self.test_runs.items()})

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
        _atomic_write(PROJECTS_FILE, [p.model_dump(mode="json") for p in self.projects.values()])
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
        _atomic_write(WEBSITES_FILE, [w.model_dump(mode="json") for w in self.websites.values()])
        return web

    # Scans
    def get_latest_scan(self, website_id: str) -> Optional[ScanResult]:
        return self.scans.get(website_id)

    def save_scan(self, website_id: str, scan: ScanResult) -> ScanResult:
        self.scans[website_id] = scan
        _atomic_write(SCANS_FILE, {k: v.model_dump(mode="json") for k, v in self.scans.items()})
        return scan

    # Test cases
    def get_test_cases(self, website_id: str) -> List[TestCase]:
        return self.test_cases.get(website_id, [])

    def save_test_cases(self, website_id: str, cases: List[TestCase]) -> List[TestCase]:
        self.test_cases[website_id] = cases
        _atomic_write(TEST_CASES_FILE, {k: [c.model_dump(mode="json") for c in v] for k, v in self.test_cases.items()})
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
        _atomic_write(TEST_RUNS_FILE, {k: v.model_dump(mode="json") for k, v in self.test_runs.items()})
        return run


storage = StorageService()
