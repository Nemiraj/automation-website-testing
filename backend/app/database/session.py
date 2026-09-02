import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.database.base import Base
from backend.app.core.logging import logger

# Setup storage directory and SQLite path
sqlite_db_path = os.path.abspath(os.path.join(settings.STORAGE_PATH, "websitetester.db"))
os.makedirs(os.path.dirname(sqlite_db_path), exist_ok=True)

# Default to SQLite for seamless zero-setup standalone local runs unless explicitly specified
use_sqlite = os.getenv("USE_SQLITE", "false").lower() == "true" or "localhost" in settings.DATABASE_URL or "127.0.0.1" in settings.DATABASE_URL

# Test connection or fallback
if use_sqlite:
    active_async_url = f"sqlite+aiosqlite:///{sqlite_db_path}"
    active_sync_url = f"sqlite:///{sqlite_db_path}"
else:
    active_async_url = settings.DATABASE_URL
    active_sync_url = settings.DATABASE_SYNC_URL

engine = create_async_engine(
    active_async_url,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

sync_engine = create_engine(
    active_sync_url,
    echo=False,
    future=True
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    class_=Session
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db() -> Session:
    db = SyncSessionLocal()
    try:
        return db
    finally:
        pass


async def init_db():
    global engine, AsyncSessionLocal
    from sqlalchemy import text
    
    def _check_and_add_columns(sync_conn):
        try:
            # Check test_runs table
            res = sync_conn.execute(text("PRAGMA table_info(test_runs)"))
            cols = [row[1] for row in res.fetchall()]
            if cols:
                if "target_type" not in cols:
                    sync_conn.execute(text("ALTER TABLE test_runs ADD COLUMN target_type VARCHAR(20) DEFAULT 'live'"))
                if "environment" not in cols:
                    sync_conn.execute(text("ALTER TABLE test_runs ADD COLUMN environment JSON DEFAULT '{}'"))
                if "ai_readiness_score" not in cols:
                    sync_conn.execute(text("ALTER TABLE test_runs ADD COLUMN ai_readiness_score FLOAT"))
                if "ai_readiness_data" not in cols:
                    sync_conn.execute(text("ALTER TABLE test_runs ADD COLUMN ai_readiness_data JSON DEFAULT '{}'"))
                if "solution_plan" not in cols:
                    sync_conn.execute(text("ALTER TABLE test_runs ADD COLUMN solution_plan JSON DEFAULT '{}'"))

            # Check issues table
            res_iss = sync_conn.execute(text("PRAGMA table_info(issues)"))
            iss_cols = [row[1] for row in res_iss.fetchall()]
            if iss_cols:
                if "issue_number" not in iss_cols:
                    sync_conn.execute(text("ALTER TABLE issues ADD COLUMN issue_number INTEGER"))
                if "section" not in iss_cols:
                    sync_conn.execute(text("ALTER TABLE issues ADD COLUMN section VARCHAR(100)"))
                if "coordinates" not in iss_cols:
                    sync_conn.execute(text("ALTER TABLE issues ADD COLUMN coordinates JSON DEFAULT '{}'"))
                if "marker_type" not in iss_cols:
                    sync_conn.execute(text("ALTER TABLE issues ADD COLUMN marker_type VARCHAR(30) DEFAULT 'rectangle'"))
                if "annotated_screenshot_url" not in iss_cols:
                    sync_conn.execute(text("ALTER TABLE issues ADD COLUMN annotated_screenshot_url VARCHAR(1024)"))
                if "source_location" not in iss_cols:
                    sync_conn.execute(text("ALTER TABLE issues ADD COLUMN source_location JSON DEFAULT '{}'"))
                if "fix_confidence" not in iss_cols:
                    sync_conn.execute(text("ALTER TABLE issues ADD COLUMN fix_confidence VARCHAR(30) DEFAULT 'high'"))
                if "fix_reasoning" not in iss_cols:
                    sync_conn.execute(text("ALTER TABLE issues ADD COLUMN fix_reasoning TEXT"))
        except Exception:
            pass

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(_check_and_add_columns)
        logger.info(f"Database schema initialized ({'SQLite: ' + sqlite_db_path if 'sqlite' in active_async_url else 'PostgreSQL'})")
    except Exception as e:
        logger.warning(f"Connection to primary DB failed ({e}). Switching to local SQLite database: {sqlite_db_path}")
        active_sqlite_async = f"sqlite+aiosqlite:///{sqlite_db_path}"
        engine = create_async_engine(active_sqlite_async, echo=False, future=True)
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(_check_and_add_columns)
        logger.info(f"Local SQLite database schema initialized at {sqlite_db_path}")
