# all database queires for the Bid model

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Bid


class BidRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, bid_id: int) -> Bid | None:
        result = await self.db.execute(select(Bid).where(Bid.id == bid_id))
        return result.scalar_one_or_none()

    async def get_by_auction(self, auction_id: int) -> list[Bid]:
        # returns all bids for an auction ordered by price descending
        # highest bid is always first
        result = await self.db.execute(
            select(Bid).where(Bid.auction_id == auction_id).order_by(Bid.price.desc())
        )
        return list(result.scalars().all())

    async def get_highest_bid(self, auction_id: int) -> Bid | None:
        # returns only the highest bid - used when closing an auction
        result = await self.db.execute(
            select(Bid)
            .where(Bid.auction_id == auction_id)
            .order_by(Bid.price.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, auction_id: int, price: float) -> Bid:
        bid = Bid(user_id=user_id, auction_id=auction_id, price=price)
        self.db.add(bid)
        await self.db.flush()
        return bid
