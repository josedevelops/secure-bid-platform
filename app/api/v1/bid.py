# bid routes - place and list bids

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.api.dependencies import get_current_user
from app.repository.bid import BidRepository
from app.repository.auction import AuctionRepository
from app.schemas.bid import BidCreate, BidResponse
from app.db.models import Bid, User, AuctionStatus


router = APIRouter(prefix="/bids", tags=["bids"])


@router.get("/auction/{auction_id}", response_model=list[BidResponse])
async def list_bids(auction_id: int, db: AsyncSession = Depends(get_db)):
    # public - anyone can see bids on an auction
    repo = BidRepository(db)
    return await repo.get_by_auction(auction_id)


@router.post("/", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def place_bid(
    body: BidCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auction_repo = AuctionRepository(db)
    auction = await auction_repo.get_by_id(body.auction_id)

    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    # only active auctions accept bids
    if auction.status != AuctionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Auction is not active")

    # seller cannot bid on their own auctions
    if auction.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot bid on your own auction")

    # bid must be higher than current highest bid
    bid_repo = BidRepository(db)
    highest = await bid_repo.get_highest_bid(body.auction_id)
    if highest and body.price <= highest.price:
        raise HTTPException(
            status_code=400, detail=f"Bid must exceed current highest: {highest.price}"
        )

    return await bid_repo.create(
        user_id=current_user.id, auction_id=body.auction_id, price=body.price
    )
