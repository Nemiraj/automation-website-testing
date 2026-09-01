from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.api.deps import get_db_session
from backend.app.models.page import Page
from backend.app.schemas.page import PageResponse

router = APIRouter()


@router.get("/{page_id}", response_model=PageResponse)
async def get_page_details(page_id: str, db: AsyncSession = Depends(get_db_session)):
    stmt = select(Page).where(Page.id == page_id)
    result = await db.execute(stmt)
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page record not found")

    return PageResponse.model_validate(page)
