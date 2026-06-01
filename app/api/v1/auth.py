# auth routes — signup and login
# we use custom exceptions from errors.py so all error responses
# have the same consistent JSON shape across the entire API
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.repository.user import UserRepository
from app.core.security import verify_password, create_access_token
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.core.errors import DuplicateResourceError, InvalidCredentialsError, InactiveAccountError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    # check for existing username and email before creating
    # we raise specific errors so the client knows exactly what conflicted
    if await repo.get_by_username(body.username):
        raise DuplicateResourceError("Username already taken")
    if await repo.get_by_email(body.email):
        raise DuplicateResourceError("Email already registered")
    user = await repo.create(
        username=body.username, email=body.email, password=body.password
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_username(body.username)
    # same error for wrong username or wrong password — prevents user enumeration
    # never tell the client whether the username exists or the password was wrong
    if not user or not verify_password(body.password, user.hashed_password):
        raise InvalidCredentialsError()
    if not user.is_active:
        raise InactiveAccountError()
    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)
