# all database queries for the User model live here
# routes call these function - never queries the db directly


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User
from app.core.security import hash_password


class UserRepository:
    def __init__(self, db: AsyncSession):
        # db session is injected - repository never creates its own session
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, username: str, email: str, password: str) -> User:
        # hash before storing password
        user = User(
            username=username, email=email, hashed_password=hash_password(password)
        )
        self.db.add(user)
        await self.db.flush()  # flush assigns the id without commiting
        return user

    async def update(self, user: User, **kwargs) -> User:
        # if password is being updated, hash it first
        if "password" in kwargs:
            kwargs["hashed_password"] = hash_password(kwargs.pop("password"))
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.db.flush()
        return user

    async def deactivate(self, user: User) -> User:
        # soft delete - never removes user record, just deactivates
        user.is_active = False
        await self.db.flush()
        return user
