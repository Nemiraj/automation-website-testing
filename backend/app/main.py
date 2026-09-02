import os
import sys
import asyncio

# On Windows, enforce ProactorEventLoopPolicy for Playwright subprocesses
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Ensure both backend directory and workspace root directory are in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for p in [root_dir, backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.api.v1.router import api_router
from backend.app.database.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    logger.info("Initializing database schemas...")
    try:
        await init_db()
        logger.info("Database schemas initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Autonomous AI-Powered Website Automation Testing Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static screenshots serving
screenshots_dir = os.path.join(settings.STORAGE_PATH, "screenshots")
diffs_dir = os.path.join(screenshots_dir, "diffs")
os.makedirs(screenshots_dir, exist_ok=True)
os.makedirs(diffs_dir, exist_ok=True)

app.mount("/api/screenshots", StaticFiles(directory=screenshots_dir), name="screenshots")
app.mount("/api/storage/screenshots", StaticFiles(directory=screenshots_dir), name="api_storage_screenshots")
app.mount("/storage/screenshots", StaticFiles(directory=screenshots_dir), name="storage_screenshots")

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
