from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl, Field


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    base_url: str = Field(..., max_length=1024)
    description: Optional[str] = None
    default_config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    description: Optional[str] = None
    default_config: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    test_runs_count: Optional[int] = 0
    latest_score: Optional[float] = None

    class Config:
        from_attributes = True
