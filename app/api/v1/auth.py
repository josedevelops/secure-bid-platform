# auth routes - signup and login

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.repository.user import UserRepository
from app.core.security import verify_password, create_access_token
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)

    # check for existing username and email before creating
    if await repo.get_by_username(body.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if await repo.get_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await repo.create(
        username=body.username, email=body.email, password=body.password
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_username(body.username)

    # same error for wrong username or wrong password - prevents user enumeration
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")

    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)
