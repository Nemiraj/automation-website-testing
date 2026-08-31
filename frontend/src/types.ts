export type BrowserType = 'chromium' | 'firefox' | 'webkit';
export type EnvironmentType = 'local' | 'staging' | 'production';
export type TestStatus = 'pending' | 'running' | 'passed' | 'failed' | 'warning' | 'skipped' | 'recovered';
export type SeverityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
export type PriorityLevel = 'P0' | 'P1' | 'P2' | 'P3';
export type FailureClassification = 'NEW_FAILURE' | 'FIXED_FAILURE' | 'CONTINUING_FAILURE' | 'NEW_WARNING';

export interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Website {
  id: string;
  projectId: string;
  name: string;
  url: string;
  environment: EnvironmentType;
  authConfig?: {
    loginUrl?: string;
    usernameField?: string;
    passwordField?: string;
    testUsername?: string;
    testPassword?: string;
  };
  crawlConfig?: {
    maxDepth: number;
    maxPages: number;
    sameOriginOnly: boolean;
    excludedPaths: string[];
    disallowedDestructiveActions: boolean;
  };
  createdAt: string;
  updatedAt: string;
}

export interface FormFieldInfo {
  name: string;
  type: string;
  label?: string;
  placeholder?: string;
  required: boolean;
  defaultValue?: string;
  options?: string[];
}

export interface DiscoveredForm {
  id: string;
  pageUrl: string;
  pageTitle: string;
  action: string;
  method: string;
  name?: string;
  fields: FormFieldInfo[];
  submitButtonText?: string;
  validationStatus: 'PASSED' | 'FAILED' | 'WARNING' | 'UNTESTED';
}

export interface ElementInfo {
  id: string;
  tagName: string;
  role?: string;
  accessibleName?: string;
  text?: string;
  inputType?: string;
  placeholder?: string;
  name?: string;
  idAttr?: string;
  className?: string;
  href?: string;
  action?: string;
  method?: string;
  required?: boolean;
  isInteractive: boolean;
  isDestructive: boolean;
  locators: {
    strategy: 'role' | 'label' | 'placeholder' | 'testid' | 'text' | 'css' | 'xpath';
    selector: string;
    confidence: number;
  }[];
}

export interface PageInfo {
  id: string;
  url: string;
  path: string;
  title: string;
  statusCode: number;
  loadTimeMs: number;
  depth: number;
  internalLinks: string[];
  externalLinks: string[];
  elements: ElementInfo[];
  formsCount: number;
  buttonsCount: number;
  inputsCount: number;
  consoleErrorsCount: number;
  networkErrorsCount: number;
  healthStatus: 'HEALTHY' | 'WARNING' | 'FAILED';
  lastScannedAt: string;
}

export interface TestStep {
  id: string;
  order: number;
  action: 'navigate' | 'click' | 'fill' | 'select' | 'check' | 'uncheck' | 'submit' | 'wait' | 'assert_text' | 'assert_url' | 'assert_visible';
  targetDescription: string;
  selector?: string;
  selectorStrategy?: string;
  value?: string;
  expectedResult: string;
  timeoutMs?: number;
  isDestructive?: boolean;
}

export interface TestCase {
  id: string;
  projectId: string;
  websiteId: string;
  name: string;
  description: string;
  category: 'authentication' | 'user_journey' | 'form' | 'search' | 'navigation' | 'buttons' | 'responsive' | 'performance';
  priority: PriorityLevel;
  severity: SeverityLevel;
  journeyName?: string;
  url: string;
  steps: TestStep[];
  isAiGenerated: boolean;
  tags?: string[];
  createdAt: string;
}

export interface StepExecutionResult {
  stepId: string;
  order: number;
  action: string;
  targetDescription: string;
  expectedResult: string;
  actualResult: string;
  status: TestStatus;
  durationMs: number;
  timestamp: string;
  screenshotUrl?: string;
  recoveryApplied?: {
    originalSelector: string;
    recoveredSelector: string;
    strategy: string;
    confidence: number;
    reason: string;
  };
  error?: {
    message: string;
    stack?: string;
    code?: string;
  };
}

export interface BrowserEvent {
  id: string;
  runId: string;
  testId?: string;
  stepId?: string;
  timestamp: string;
  type: 'navigation' | 'click' | 'fill' | 'console' | 'page_error' | 'network_request' | 'network_response' | 'network_failure' | 'dialog' | 'screenshot' | 'recovery';
  target?: string;
  url?: string;
  status?: string;
  payload?: any;
}

export interface NetworkEvent {
  id: string;
  runId: string;
  testId?: string;
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'OPTIONS';
  status: number;
  durationMs: number;
  resourceType: string;
  isFailed: boolean;
  requestHeaders?: Record<string, string>;
  responseHeaders?: Record<string, string>;
  requestBody?: string;
  responseBody?: string;
  errorMessage?: string;
  timestamp: string;
}

export interface ConsoleEvent {
  id: string;
  runId: string;
  testId?: string;
  type: 'log' | 'info' | 'warning' | 'error' | 'debug';
  text: string;
  location?: string;
  timestamp: string;
}

export interface UserJourneyStep {
  name: string;
  pageUrl: string;
  action: string;
  expected: string;
  status: TestStatus;
  durationMs: number;
}

export interface UserJourneyResult {
  id: string;
  name: string;
  category: string;
  status: TestStatus;
  durationMs: number;
  failedStepName?: string;
  failedStepIndex?: number;
  totalSteps: number;
  completedSteps: number;
  businessImpactScore: number;
  steps: UserJourneyStep[];
}

export interface AiFailureAnalysis {
  id: string;
  testId: string;
  summary: string;
  confirmedFacts: string[];
  aiEstimatedCauses: string[];
  likelyCause: string;
  confidence: 'High' | 'Medium' | 'Low';
  confidenceScore: number;
  userImpact: string;
  businessImpactScore: number;
  businessImpactFactors: {
    factor: string;
    weight: number;
    description: string;
  }[];
  recommendedInvestigation: string[];
  suggestedFix?: string;
  whereToFix?: string;
  whatToFix?: string;
  codeSnippetFix?: string;
}

export interface FailureInvestigation {
  id: string;
  testRunId: string;
  testId: string;
  testName: string;
  journeyName?: string;
  severity: SeverityLevel;
  priority: PriorityLevel;
  failedStepIndex: number;
  totalSteps: number;
  failedPageUrl: string;
  userAction: string;
  expected: string;
  actual: string;
  businessImpactSummary: string;
  businessImpactScore: number;
  screenshotUrl?: string;
  screenshotBaselineUrl?: string;
  traceUrl?: string;
  relatedApiFailures: NetworkEvent[];
  relatedConsoleErrors: ConsoleEvent[];
  timeline: {
    time: string;
    label: string;
    status: TestStatus;
    type: string;
    details?: string;
  }[];
  aiAnalysis: AiFailureAnalysis;
  rootCauseGroupId?: string;
}

export interface FailureGroup {
  id: string;
  title: string;
  rootCauseType: 'API_5XX' | 'API_4XX' | 'JS_CRASH' | 'TIMEOUT' | 'ELEMENT_NOT_FOUND' | 'ASSERTION_MISMATCH';
  primaryEvidence: string;
  affectedCount: number;
  affectedTestIds: string[];
  affectedTestNames: string[];
  severity: SeverityLevel;
  impactScore: number;
}

export interface TestResult {
  id: string;
  runId: string;
  testCaseId: string;
  testName: string;
  category: string;
  priority: PriorityLevel;
  severity: SeverityLevel;
  journeyName?: string;
  url: string;
  status: TestStatus;
  durationMs: number;
  totalSteps: number;
  passedSteps: number;
  stepResults: StepExecutionResult[];
  failureInvestigation?: FailureInvestigation;
  screenshotUrl?: string;
}

export interface PerformanceMetrics {
  pageLoadTimeMs: number;
  domContentLoadedMs: number;
  firstContentfulPaintMs?: number;
  totalRequests: number;
  transferSizeBytes: number;
}

export interface TestRun {
  id: string;
  projectId: string;
  websiteId: string;
  websiteUrl: string;
  browser: BrowserType;
  environment: EnvironmentType;
  viewport: { width: number; height: number };
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  healthScore: number;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  warningTests: number;
  skippedTests: number;
  criticalFailures: number;
  pagesTestedCount: number;
  apiFailuresCount: number;
  jsErrorsCount: number;
  durationMs: number;
  startedAt: string;
  completedAt?: string;
  results: TestResult[];
  userJourneys: UserJourneyResult[];
  failureGroups: FailureGroup[];
  networkEvents: NetworkEvent[];
  consoleEvents: ConsoleEvent[];
  performanceMetrics?: PerformanceMetrics;
  regressionSummary?: {
    newFailures: number;
    fixedFailures: number;
    continuingFailures: number;
    newWarnings: number;
    previousRunId?: string;
    previousHealthScore?: number;
  };
}

export interface ScanResult {
  websiteId: string;
  rootUrl: string;
  scannedAt: string;
  totalPages: number;
  totalLinks: number;
  totalButtons: number;
  totalForms: number;
  totalInputs: number;
  pages: PageInfo[];
  siteMapTree: {
    url: string;
    path: string;
    title: string;
    status: 'HEALTHY' | 'WARNING' | 'FAILED';
    children: any[];
  };
}
