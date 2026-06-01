# profile routes — view and update own profile
# we use custom exceptions from errors.py so all error responses
# have consistent JSON shape across the entire API
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.api.dependencies import get_current_user
from app.repository.user import UserRepository
from app.schemas.profile import ProfileUpdate, PasswordChange, ProfileResponse
from app.db.models import User
from app.core.security import verify_password
from app.core.errors import DuplicateResourceError, BadRequestError

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    # no db call needed — current_user is already loaded by the dependency
    return current_user


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    body: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    if body.username:
        existing = await repo.get_by_username(body.username)
        if existing and existing.id != current_user.id:
            raise DuplicateResourceError("Username already taken")
    if body.email:
        existing = await repo.get_by_email(body.email)
        if existing and existing.id != current_user.id:
            raise DuplicateResourceError("Email already registered")
    return await repo.update(current_user, **body.model_dump(exclude_none=True))


@router.post("/me/password")
async def change_password(
    body: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(body.current_password, current_user.hashed_password):
        raise BadRequestError("Current password is incorrect")
    repo = UserRepository(db)
    await repo.update(current_user, password=body.new_password)
    return {"message": "Password updated successfully"}
