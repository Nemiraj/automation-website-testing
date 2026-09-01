from fastapi import APIRouter
from backend.app.api.v1 import projects, tests, pages, issues, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(tests.router, prefix="/tests", tags=["Tests"])
api_router.include_router(pages.router, prefix="/pages", tags=["Pages"])
api_router.include_router(issues.router, prefix="/issues", tags=["Issues"])
