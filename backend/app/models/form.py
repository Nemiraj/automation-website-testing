import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class Form(Base):
    __tablename__ = "forms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False)
    page_id: Mapped[str] = mapped_column(String(36), ForeignKey("pages.id", ondelete="CASCADE"), nullable=True)
    page_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    
    selector: Mapped[str] = mapped_column(String(512), nullable=False)
    action: Mapped[str] = mapped_column(String(1024), nullable=True)
    method: Mapped[str] = mapped_column(String(20), default="POST")
    fields: Mapped[list] = mapped_column(JSON, default=list)
    has_submit_button: Mapped[bool] = mapped_column(Boolean, default=True)
    has_validation: Mapped[bool] = mapped_column(Boolean, default=False)
    validation_results: Mapped[dict] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("TestRun", back_populates="forms")
    page = relationship("Page", back_populates="forms")
