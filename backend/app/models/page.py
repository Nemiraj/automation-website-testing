import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, default=200)
    title: Mapped[str] = mapped_column(String(512), nullable=True)
    meta_description: Mapped[str] = mapped_column(String(1024), nullable=True)
    canonical_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    
    # Counts
    links_count: Mapped[int] = mapped_column(Integer, default=0)
    images_count: Mapped[int] = mapped_column(Integer, default=0)
    forms_count: Mapped[int] = mapped_column(Integer, default=0)
    buttons_count: Mapped[int] = mapped_column(Integer, default=0)
    scripts_count: Mapped[int] = mapped_column(Integer, default=0)
    stylesheets_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Performance metrics
    load_time_ms: Mapped[float] = mapped_column(Float, nullable=True)
    dom_content_loaded_ms: Mapped[float] = mapped_column(Float, nullable=True)
    first_contentful_paint_ms: Mapped[float] = mapped_column(Float, nullable=True)
    transfer_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Headings hierarchy & metadata
    headings: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("TestRun", back_populates="pages")
    issues = relationship("Issue", back_populates="page", cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="page", cascade="all, delete-orphan")
    forms = relationship("Form", back_populates="page", cascade="all, delete-orphan")
