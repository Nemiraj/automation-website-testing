from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class FormField(BaseModel):
    name: Optional[str] = None
    type: str = "text"
    required: bool = False
    placeholder: Optional[str] = None
    label: Optional[str] = None


class FormResponse(BaseModel):
    id: str
    test_run_id: str
    page_id: Optional[str] = None
    page_url: str
    selector: str
    action: Optional[str] = None
    method: str = "POST"
    fields: List[Dict[str, Any]] = Field(default_factory=list)
    has_submit_button: bool = True
    has_validation: bool = False
    validation_results: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True
