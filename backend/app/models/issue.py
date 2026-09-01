import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False)
    page_id: Mapped[str] = mapped_column(String(36), ForeignKey("pages.id", ondelete="CASCADE"), nullable=True)
    page_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    
    # Category: UI, Responsive, Functional, Forms, Accessibility, Performance, SEO, JavaScript, Network, Visual Regression
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Severity: Critical, High, Medium, Low, Info
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_matters: Mapped[str] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    suggested_fix: Mapped[str] = mapped_column(Text, nullable=True)
    
    selector: Mapped[str] = mapped_column(String(512), nullable=True)
    viewport: Mapped[str] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open")  # open, resolved, ignored
    
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    screenshot_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("TestRun", back_populates="issues")
    page = relationship("Page", back_populates="issues")
