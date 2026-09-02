import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class TestRun(Base):
    __tablename__ = "test_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    target_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, running, completed, failed, cancelled
    
    # Progress info
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    current_stage: Mapped[str] = mapped_column(String(100), default="queued")
    current_page_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    error_message: Mapped[str] = mapped_column(String(1024), nullable=True)

    # Target & Environment
    target_type: Mapped[str] = mapped_column(String(20), default="live")  # live | localhost
    environment: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Config options
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Deterministic Scores (0-100)
    overall_score: Mapped[float] = mapped_column(Float, nullable=True)
    ui_score: Mapped[float] = mapped_column(Float, nullable=True)
    responsive_score: Mapped[float] = mapped_column(Float, nullable=True)
    functional_score: Mapped[float] = mapped_column(Float, nullable=True)
    forms_score: Mapped[float] = mapped_column(Float, nullable=True)
    accessibility_score: Mapped[float] = mapped_column(Float, nullable=True)
    performance_score: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Metric counts
    total_pages_scanned: Mapped[int] = mapped_column(Integer, default=0)
    critical_issues_count: Mapped[int] = mapped_column(Integer, default=0)
    high_issues_count: Mapped[int] = mapped_column(Integer, default=0)
    medium_issues_count: Mapped[int] = mapped_column(Integer, default=0)
    low_issues_count: Mapped[int] = mapped_column(Integer, default=0)
    info_issues_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="test_runs")
    pages = relationship("Page", back_populates="test_run", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="test_run", cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="test_run", cascade="all, delete-orphan")
    forms = relationship("Form", back_populates="test_run", cascade="all, delete-orphan")
    ai_analysis = relationship("AIAnalysis", back_populates="test_run", uselist=False, cascade="all, delete-orphan")
