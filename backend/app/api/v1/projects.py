from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from backend.app.api.deps import get_db_session
from backend.app.models.project import Project
from backend.app.models.test_run import TestRun
from backend.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from backend.app.core.security import validate_target_url

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db_session)):
    is_valid, msg_or_url = validate_target_url(payload.base_url)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg_or_url)

    project = Project(
        name=payload.name,
        base_url=msg_or_url,
        description=payload.description,
        default_config=payload.default_config or {}
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        base_url=project.base_url,
        description=project.description,
        default_config=project.default_config,
        user_id=project.user_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        test_runs_count=0,
        latest_score=None
    )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db_session)):
    stmt = select(Project).order_by(desc(Project.created_at))
    result = await db.execute(stmt)
    projects = result.scalars().all()

    response = []
    for p in projects:
        # Get count and latest score
        runs_stmt = select(TestRun).where(TestRun.project_id == p.id).order_by(desc(TestRun.created_at))
        runs_res = await db.execute(runs_stmt)
        runs = runs_res.scalars().all()
        
        runs_count = len(runs)
        latest_score = runs[0].overall_score if runs and runs[0].overall_score is not None else None

        response.append(ProjectResponse(
            id=p.id,
            name=p.name,
            base_url=p.base_url,
            description=p.description,
            default_config=p.default_config,
            user_id=p.user_id,
            created_at=p.created_at,
            updated_at=p.updated_at,
            test_runs_count=runs_count,
            latest_score=latest_score
        ))

    return response


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    p = result.scalar_one_or_none()

    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    runs_stmt = select(TestRun).where(TestRun.project_id == p.id).order_by(desc(TestRun.created_at))
    runs_res = await db.execute(runs_stmt)
    runs = runs_res.scalars().all()

    return ProjectResponse(
        id=p.id,
        name=p.name,
        base_url=p.base_url,
        description=p.description,
        default_config=p.default_config,
        user_id=p.user_id,
        created_at=p.created_at,
        updated_at=p.updated_at,
        test_runs_count=len(runs),
        latest_score=runs[0].overall_score if runs and runs[0].overall_score is not None else None
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    p = result.scalar_one_or_none()

    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    await db.delete(p)
    await db.commit()
    return None
