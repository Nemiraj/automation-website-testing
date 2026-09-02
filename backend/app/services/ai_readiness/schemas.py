from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CategoryScore(BaseModel):
    category_id: str
    name: str
    score: float
    weight: float
    passed_checks: int
    total_checks: int
    findings: List[Dict[str, Any]] = Field(default_factory=list)


class EntityConsistency(BaseModel):
    is_consistent: bool
    detected_names: List[str] = Field(default_factory=list)
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None
    social_profiles: List[str] = Field(default_factory=list)
    inconsistencies: List[str] = Field(default_factory=list)


class StructuredDataAudit(BaseModel):
    found: bool
    types_detected: List[str] = Field(default_factory=list)
    schemas: List[Dict[str, Any]] = Field(default_factory=list)
    syntax_errors: List[str] = Field(default_factory=list)
    missing_recommended_types: List[str] = Field(default_factory=list)
    generated_jsonld_sample: Optional[Dict[str, Any]] = None


class AIReadinessRecommendation(BaseModel):
    priority: str  # critical, high, medium, low
    category: str
    title: str
    evidence: str
    why_it_matters: str
    action: str
    code_fix: Optional[str] = None


class AIReadinessReport(BaseModel):
    overall_score: float
    environment_type: str  # "LIVE WEBSITE" | "LOCAL DEVELOPMENT"
    category_scores: Dict[str, CategoryScore] = Field(default_factory=dict)
    entity_consistency: Optional[EntityConsistency] = None
    structured_data: Optional[StructuredDataAudit] = None
    top_improvements: List[AIReadinessRecommendation] = Field(default_factory=list)
    rendering_dependency: Dict[str, Any] = Field(default_factory=dict)
    crawlability_summary: Dict[str, Any] = Field(default_factory=dict)
    agent_accessibility: Dict[str, Any] = Field(default_factory=dict)
