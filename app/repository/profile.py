# profile repository reuses UserRepository - Profile operations are user ops.
# this file handles the read side of profile data

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User
from app.db.models import MemberType


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[User]:
        # admi only - returns all users in the system
        result = await self.db.execute(select(User))
        return list(result.scalars().all())

    async def get_by_member_type(self, member_type: MemberType) -> list[User]:
        # filter user by role - useful for admin management views
        result = await self.db.execute(
            select(User).where(User.member_type == member_type)
        )
        return list(result.scalars().all())

    async def get_active_sellers(self) -> list[User]:
        # returns only active sellers - used for auction listing queries
        result = await self.db.execute(
            select(User).where(
                User.member_type == MemberType.SELLER, User.is_active == True
            )
        )
        return list(result.scalars().all())
