# all database queries for the auction model live here
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Auction, AuctionStatus
from typing import Optional


class AuctionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, auction_id: int) -> Auction | None:
        result = await self.db.execute(select(Auction).where(Auction.id == auction_id))
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Auction]:
        # only returns active auctions to the public listing
        result = await self.db.execute(
            select(Auction).where(Auction.status == AuctionStatus.ACTIVE)
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: int) -> list[Auction]:
        result = await self.db.execute(
            select(Auction).where(Auction.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, user_id: int, **kwargs) -> Auction:
        auction = Auction(user_id=user_id, **kwargs)
        self.db.add(auction)
        await self.db.flush()
        return auction

    async def update(self, auction: Auction, **kwargs) -> Auction:
        for key, value in kwargs.items():
            setattr(auction, key, value)
        await self.db.flush()
        return auction

    async def close(self, auction: Auction) -> Auction:
        # closes the auction - no more bids accepted after this
        auction.status = AuctionStatus.CLOSED
        await self.db.flush()
        return auction
