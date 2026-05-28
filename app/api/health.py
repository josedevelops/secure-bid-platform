# health checkpoint - used by Docker, load balancers, and monitoring tools
# returns 200 when the app is running, 503 when dependencies are down
from fastapi import APIRouter
from sqlalchemy import text
from app.db.base import AsyncSessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    db_status = "unavailable"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_status = "ok"
    except Exception as e:
        print(f"DB health check failed: {e}")

    status = "ok" if db_status == "ok" else "degraded"
    return {"status": status, "database": db_status}
