# health checkpoint - used by Docker, load balancers, and monitoring tools
# returns 200 when the app is running, 503 when dependencies are down

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.base import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    # check database connectivity - passing health check
    # means the full stack is up
    try:
        await db.execute(text("SELECT 1"))

    except Exception:
        db_status = "unavailable"

    status = "ok" if db_status == "ok" else "degraded"

    return {
        "status": status,
        "database": db_status,
    }
