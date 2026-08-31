from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

BrowserType = Literal['chromium', 'firefox', 'webkit']
EnvironmentType = Literal['local', 'staging', 'production']
TestStatus = Literal['pending', 'running', 'passed', 'failed', 'warning', 'skipped', 'recovered']
SeverityLevel = Literal['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
PriorityLevel = Literal['P0', 'P1', 'P2', 'P3']
FailureClassification = Literal['NEW_FAILURE', 'FIXED_FAILURE', 'CONTINUING_FAILURE', 'NEW_WARNING']


class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class AuthConfig(BaseModel):
    loginUrl: Optional[str] = None
    usernameField: Optional[str] = None
    passwordField: Optional[str] = None
    testUsername: Optional[str] = None
    testPassword: Optional[str] = None


class CrawlConfig(BaseModel):
    maxDepth: int = 3
    maxPages: int = 15
    sameOriginOnly: bool = True
    excludedPaths: List[str] = Field(default_factory=list)
    disallowedDestructiveActions: bool = True


class Website(BaseModel):
    id: str
    projectId: str
    name: str
    url: str
    environment: EnvironmentType = "local"
    authConfig: Optional[AuthConfig] = None
    crawlConfig: Optional[CrawlConfig] = None
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class GeneratedLocator(BaseModel):
    strategy: Literal['role', 'label', 'placeholder', 'testid', 'text', 'css', 'xpath']
    selector: str
    confidence: float


class ElementInfo(BaseModel):
    id: str
    tagName: str
    role: Optional[str] = None
    accessibleName: Optional[str] = None
    text: Optional[str] = None
    inputType: Optional[str] = None
    placeholder: Optional[str] = None
    name: Optional[str] = None
    idAttr: Optional[str] = None
    className: Optional[str] = None
    href: Optional[str] = None
    action: Optional[str] = None
    method: Optional[str] = None
    required: bool = False
    isInteractive: bool = False
    isDestructive: bool = False
    locators: List[GeneratedLocator] = Field(default_factory=list)


class PageInfo(BaseModel):
    id: str
    url: str
    path: str
    title: str
    statusCode: int
    loadTimeMs: int
    depth: int
    internalLinks: List[str] = Field(default_factory=list)
    externalLinks: List[str] = Field(default_factory=list)
    elements: List[ElementInfo] = Field(default_factory=list)
    formsCount: int = 0
    buttonsCount: int = 0
    inputsCount: int = 0
    consoleErrorsCount: int = 0
    networkErrorsCount: int = 0
    healthStatus: str = 'HEALTHY'
    lastScannedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class SiteMapNode(BaseModel):
    url: str
    path: str
    title: str
    status: str = 'HEALTHY'
    children: List[Any] = Field(default_factory=list)


class ScanResult(BaseModel):
    websiteId: str
    rootUrl: str
    scannedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    totalPages: int = 0
    totalLinks: int = 0
    totalButtons: int = 0
    totalForms: int = 0
    totalInputs: int = 0
    pages: List[PageInfo] = Field(default_factory=list)
    siteMapTree: SiteMapNode


class TestStep(BaseModel):
    id: str
    order: int
    action: str = "navigate"
    targetDescription: str
    selector: Optional[str] = None
    selectorStrategy: Optional[str] = None
    value: Optional[str] = None
    expectedResult: str
    timeoutMs: Optional[int] = 5000
    isDestructive: Optional[bool] = False


class TestCase(BaseModel):
    id: str
    projectId: str
    websiteId: str
    name: str
    description: str
    category: str = "functional"
    priority: PriorityLevel = "P1"
    severity: SeverityLevel = "HIGH"
    journeyName: Optional[str] = None
    url: str
    steps: List[TestStep] = Field(default_factory=list)
    isAiGenerated: bool = True
    tags: Optional[List[str]] = Field(default_factory=list)
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class StepRecoveryInfo(BaseModel):
    originalSelector: str
    recoveredSelector: str
    strategy: str
    confidence: float
    reason: str


class StepError(BaseModel):
    message: str
    stack: Optional[str] = None
    code: Optional[str] = None


class StepExecutionResult(BaseModel):
    stepId: str
    order: int
    action: str
    targetDescription: str
    expectedResult: str
    actualResult: str
    status: TestStatus
    durationMs: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    screenshotUrl: Optional[str] = None
    recoveryApplied: Optional[StepRecoveryInfo] = None
    error: Optional[StepError] = None


class NetworkEvent(BaseModel):
    id: str
    runId: str
    testId: Optional[str] = None
    url: str
    method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    status: int
    durationMs: int = 0
    resourceType: str = "xhr"
    isFailed: bool = False
    requestHeaders: Optional[Dict[str, str]] = None
    responseHeaders: Optional[Dict[str, str]] = None
    requestBody: Optional[str] = None
    responseBody: Optional[str] = None
    errorMessage: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ConsoleEvent(BaseModel):
    id: str
    runId: str
    testId: Optional[str] = None
    type: Literal['log', 'info', 'warning', 'error', 'debug'] = "log"
    text: str
    location: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class BrowserEvent(BaseModel):
    id: str
    runId: str
    testId: Optional[str] = None
    stepId: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    type: str
    target: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = None
    payload: Optional[Any] = None


class BusinessImpactFactor(BaseModel):
    factor: str
    weight: int
    description: str


class AiFailureAnalysis(BaseModel):
    id: str
    testId: str
    summary: str
    confirmedFacts: List[str] = Field(default_factory=list)
    aiEstimatedCauses: List[str] = Field(default_factory=list)
    likelyCause: str
    confidence: Literal['High', 'Medium', 'Low'] = "High"
    confidenceScore: float = 0.9
    userImpact: str
    businessImpactScore: int = 0
    businessImpactFactors: List[BusinessImpactFactor] = Field(default_factory=list)
    recommendedInvestigation: List[str] = Field(default_factory=list)
    suggestedFix: Optional[str] = None
    whereToFix: Optional[str] = None
    whatToFix: Optional[str] = None
    codeSnippetFix: Optional[str] = None


class FailureTimelineItem(BaseModel):
    time: str
    label: str
    status: TestStatus
    type: str
    details: Optional[str] = None


class FailureInvestigation(BaseModel):
    id: str
    testRunId: str
    testId: str
    testName: str
    journeyName: Optional[str] = None
    severity: SeverityLevel
    priority: PriorityLevel
    failedStepIndex: int
    totalSteps: int
    failedPageUrl: str
    userAction: str
    expected: str
    actual: str
    businessImpactSummary: str
    businessImpactScore: int
    screenshotUrl: Optional[str] = None
    screenshotBaselineUrl: Optional[str] = None
    traceUrl: Optional[str] = None
    relatedApiFailures: List[NetworkEvent] = Field(default_factory=list)
    relatedConsoleErrors: List[ConsoleEvent] = Field(default_factory=list)
    timeline: List[FailureTimelineItem] = Field(default_factory=list)
    aiAnalysis: AiFailureAnalysis
    rootCauseGroupId: Optional[str] = None


class FailureGroup(BaseModel):
    id: str
    title: str
    rootCauseType: Literal['API_5XX', 'API_4XX', 'JS_CRASH', 'TIMEOUT', 'ELEMENT_NOT_FOUND', 'ASSERTION_MISMATCH']
    primaryEvidence: str
    affectedCount: int
    affectedTestIds: List[str]
    affectedTestNames: List[str]
    severity: SeverityLevel
    impactScore: int


class TestResult(BaseModel):
    id: str
    runId: str
    testCaseId: str
    testName: str
    category: str
    priority: PriorityLevel
    severity: SeverityLevel
    journeyName: Optional[str] = None
    url: str
    status: TestStatus
    durationMs: int
    totalSteps: int
    passedSteps: int
    stepResults: List[StepExecutionResult] = Field(default_factory=list)
    failureInvestigation: Optional[FailureInvestigation] = None
    screenshotUrl: Optional[str] = None


class UserJourneyStep(BaseModel):
    name: str
    pageUrl: str
    action: str
    expected: str
    status: TestStatus
    durationMs: int


class UserJourneyResult(BaseModel):
    id: str
    name: str
    category: str
    status: TestStatus
    durationMs: int
    failedStepName: Optional[str] = None
    failedStepIndex: Optional[int] = None
    totalSteps: int
    completedSteps: int
    businessImpactScore: int
    steps: List[UserJourneyStep] = Field(default_factory=list)


class PerformanceMetrics(BaseModel):
    pageLoadTimeMs: int
    domContentLoadedMs: int
    firstContentfulPaintMs: Optional[int] = None
    totalRequests: int
    transferSizeBytes: int


class RegressionSummary(BaseModel):
    newFailures: int
    fixedFailures: int
    continuingFailures: int
    newWarnings: int
    previousRunId: Optional[str] = None
    previousHealthScore: Optional[int] = None


class Viewport(BaseModel):
    width: int = 1280
    height: int = 800


class TestRun(BaseModel):
    id: str
    projectId: str
    websiteId: str
    websiteUrl: str
    browser: BrowserType = "chromium"
    environment: EnvironmentType = "local"
    viewport: Viewport = Field(default_factory=Viewport)
    status: Literal['pending', 'running', 'completed', 'failed', 'cancelled'] = "completed"
    healthScore: int = 100
    totalTests: int = 0
    passedTests: int = 0
    failedTests: int = 0
    warningTests: int = 0
    skippedTests: int = 0
    criticalFailures: int = 0
    pagesTestedCount: int = 0
    apiFailuresCount: int = 0
    jsErrorsCount: int = 0
    durationMs: int = 0
    startedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    completedAt: Optional[str] = None
    results: List[TestResult] = Field(default_factory=list)
    userJourneys: List[UserJourneyResult] = Field(default_factory=list)
    failureGroups: List[FailureGroup] = Field(default_factory=list)
    networkEvents: List[NetworkEvent] = Field(default_factory=list)
    consoleEvents: List[ConsoleEvent] = Field(default_factory=list)
    performanceMetrics: Optional[PerformanceMetrics] = None
    regressionSummary: Optional[RegressionSummary] = None
