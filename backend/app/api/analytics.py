from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.service import (
    get_analytics_records,
    get_performance_summary,
)
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_performance_summary()


@router.get("/records")
async def get_analytics_execution_records(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_analytics_records()