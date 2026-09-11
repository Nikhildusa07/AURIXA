from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User
from app.monitoring.service import get_monitoring_summary


router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"],
)


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_monitoring_summary(db)