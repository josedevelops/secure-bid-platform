# admin routes - user management, only accessible to admins


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.api.dependencies import get_current_admin
from app.repository.user import UserRepository
from app.repository.profile import ProfileRepository
from app.schemas.profile import ProfileResponse
from app.db.models import User


router = APIRouter(prefilx="/admin", tags=["admin"])


@router.get("/users", response_model=list[ProfileResponse])
async def list_users(
    db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin)
):
    repo = ProfileRepository(db)

    return await repo.get_all()


@router.post("/users/{user_id}/deactivate", response_model=ProfileResponse)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    repo = UserRepository(db)

    user = await repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate this account")

    return await repo.deactivate(user)
