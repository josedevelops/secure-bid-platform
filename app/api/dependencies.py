# shared dependencies injected into routes via FastAPI's Depends
# this keeps auth logic out of individual route handlers
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.core.security import decode_access_token
from app.repository.user import UserRepository
from app.db.models import User, MemberType
from app.core.errors import InvalidCredentialsError, AdminRequiredError

# tells FastAPI where clients send their token
# tokenUrl is the login endpoint — used by the Swagger UI to show the auth button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    # decodes the JWT and returns the user — raises 401 if invalid or expired
    subject = decode_access_token(token)
    if subject is None:
        raise InvalidCredentialsError()

    repo = UserRepository(db)
    user = await repo.get_by_username(subject)

    # we treat missing user and inactive user the same way — vague on purpose
    # never tell the client whether the user doesn't exist or is just deactivated
    if user is None or not user.is_active:
        raise InvalidCredentialsError()

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    # layers on top of get_current_user — adds admin role check
    if current_user.member_type != MemberType.ADMIN:
        raise AdminRequiredError()
    return current_user
