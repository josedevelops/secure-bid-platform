# shared dependencies injected into routes via FastApi's Depends
# this keeps auth logic out of individual route handlers

from sqlalchemy.sql.functions import current_user
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.core.security import decode_access_token
from app.repository.user import UserRepository
from app.db.models import User, MemberType


# tells FastApi where clients send their token
# tokenUrl is the login endpoint

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    # decodes the JWT and returns the user -  raises 401 if invalid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    subject = decode_access_token(token)
    if subject is None:
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_by_username(subject)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    # layers on top of get_current_user - adds admin role check
    if current_user.member_type != MemberType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detial="Admin access required"
        )
    return current_user
