from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class PageBase(BaseModel):
    url: str
    status_code: int = 200
    title: Optional[str] = None
    meta_description: Optional[str] = None
    canonical_url: Optional[str] = None
    links_count: int = 0
    images_count: int = 0
    forms_count: int = 0
    buttons_count: int = 0
    scripts_count: int = 0
    stylesheets_count: int = 0
    load_time_ms: Optional[float] = None
    dom_content_loaded_ms: Optional[float] = None
    first_contentful_paint_ms: Optional[float] = None
    transfer_size_bytes: int = 0
    headings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    raw_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PageResponse(PageBase):
    id: str
    test_run_id: str
    created_at: datetime

    class Config:
        from_attributes = True
