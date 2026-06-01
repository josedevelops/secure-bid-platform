# admin routes — user management, only accessible to admins
# we use custom exceptions from errors.py so all error responses
# have consistent JSON shape across the entire API
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.api.dependencies import get_current_admin
from app.repository.user import UserRepository
from app.repository.profile import ProfileRepository
from app.schemas.profile import ProfileResponse
from app.db.models import User
from app.core.errors import NotFoundError, BadRequestError

router = APIRouter(prefix="/admin", tags=["admin"])


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
        raise NotFoundError("User not found")
    # admin cannot deactivate their own account — prevents accidental lockout
    if user.id == current_admin.id:
        raise BadRequestError("Cannot deactivate your own account")
    return await repo.deactivate(user)
