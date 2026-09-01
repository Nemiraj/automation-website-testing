export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';

export type Category = 
  | 'ui'
  | 'responsive'
  | 'functional'
  | 'forms'
  | 'accessibility'
  | 'performance'
  | 'javascript'
  | 'network'
  | 'visual_regression';

export interface TestConfig {
  max_pages: number;
  timeout_ms: number;
  viewports: string[];
  enable_ui: boolean;
  enable_responsive: boolean;
  enable_links: boolean;
  enable_images: boolean;
  enable_javascript: boolean;
  enable_forms: boolean;
  enable_accessibility: boolean;
  enable_performance: boolean;
  enable_screenshots: boolean;
  enable_ai: boolean;
  form_submission_mode: 'validation_only' | 'synthetic_submit';
}

export interface Project {
  id: string;
  name: string;
  base_url: string;
  description?: string;
  default_config: Record<string, any>;
  created_at: string;
  updated_at: string;
  test_runs_count: number;
  latest_score?: number | null;
}

export interface TestRun {
  id: string;
  project_id?: string;
  target_url: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress_percentage: number;
  current_stage: string;
  current_page_url?: string;
  error_message?: string;
  overall_score?: number | null;
  ui_score?: number | null;
  responsive_score?: number | null;
  functional_score?: number | null;
  forms_score?: number | null;
  accessibility_score?: number | null;
  performance_score?: number | null;
  total_pages_scanned: number;
  critical_issues_count: number;
  high_issues_count: number;
  medium_issues_count: number;
  low_issues_count: number;
  info_issues_count: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface IssueItem {
  id: string;
  test_run_id: string;
  page_id?: string;
  page_url: string;
  category: Category;
  severity: Severity;
  title: string;
  description: string;
  why_it_matters?: string;
  recommendation?: string;
  suggested_fix?: string;
  selector?: string;
  viewport?: string;
  status: 'open' | 'resolved' | 'ignored';
  evidence: Record<string, any>;
  screenshot_url?: string;
  created_at: string;
}

export interface PageItem {
  id: string;
  test_run_id: string;
  url: string;
  status_code: number;
  title?: string;
  meta_description?: string;
  canonical_url?: string;
  links_count: number;
  images_count: number;
  forms_count: number;
  buttons_count: number;
  scripts_count: number;
  stylesheets_count: number;
  load_time_ms?: number;
  dom_content_loaded_ms?: number;
  first_contentful_paint_ms?: number;
  transfer_size_bytes: number;
  headings: Record<string, string[]>;
  raw_metrics: Record<string, any>;
  created_at: string;
}

export interface FormItem {
  id: string;
  test_run_id: string;
  page_id?: string;
  page_url: string;
  selector: string;
  action?: string;
  method: string;
  fields: Array<{
    name?: string;
    type: string;
    required: boolean;
    placeholder?: string;
    label?: string;
  }>;
  has_submit_button: boolean;
  has_validation: boolean;
  validation_results: Record<string, any>;
  created_at: string;
}

export interface ScreenshotItem {
  id: string;
  test_run_id: string;
  page_id?: string;
  page_url: string;
  viewport: string;
  width: number;
  height: number;
  url_path: string;
  is_full_page: boolean;
  created_at: string;
}

export interface AIAnalysisItem {
  id: string;
  test_run_id: string;
  summary: string;
  issues_analysis: Array<{
    title: string;
    severity: string;
    category: string;
    why: string;
    recommendation: string;
    suggested_fix?: string;
  }>;
  priority_actions: string[];
  model_used: string;
  created_at: string;
}

export interface ScoreBreakdown {
  overall: number;
  ui: number;
  responsive: number;
  functional: number;
  forms: number;
  accessibility: number;
  performance: number;
}

export interface TestReport {
  test_run: TestRun;
  scores: ScoreBreakdown;
  issue_counts_by_severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
    total: number;
  };
  issue_counts_by_category: {
    ui: number;
    responsive: number;
    functional: number;
    forms: number;
    accessibility: number;
    performance: number;
    javascript: number;
    network: number;
    visual_regression: number;
  };
  issues: IssueItem[];
  pages: PageItem[];
  forms: FormItem[];
  screenshots: ScreenshotItem[];
  ai_analysis?: AIAnalysisItem | null;
  previous_test_run?: TestRun | null;
}
