from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ScreenshotResponse(BaseModel):
    id: str
    test_run_id: str
    page_id: Optional[str] = None
    page_url: str
    viewport: str
    width: int
    height: int
    url_path: str
    is_full_page: bool
    created_at: datetime

    class Config:
        from_attributes = True
