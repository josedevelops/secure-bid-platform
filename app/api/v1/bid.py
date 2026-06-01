# bid routes — place and list bids
# we use custom exceptions from errors.py so all error responses
# have consistent JSON shape across the entire API
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.api.dependencies import get_current_user
from app.repository.bid import BidRepository
from app.repository.auction import AuctionRepository
from app.schemas.bid import BidCreate, BidResponse
from app.db.models import User, AuctionStatus
from app.core.errors import NotFoundError, AuctionNotActiveError, SelfBidError, BidToLowError

router = APIRouter(prefix="/bids", tags=["bids"])


@router.get("/auction/{auction_id}", response_model=list[BidResponse])
async def list_bids(auction_id: int, db: AsyncSession = Depends(get_db)):
    # public — anyone can see bids on an auction
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
        raise NotFoundError("Auction not found")
    # only active auctions accept bids — closed/cancelled auctions are frozen
    if auction.status != AuctionStatus.ACTIVE:
        raise AuctionNotActiveError()
    # seller cannot bid on their own auction — prevents wash trading
    if auction.user_id == current_user.id:
        raise SelfBidError()
    # bid must exceed current highest bid — enforces auction integrity
    bid_repo = BidRepository(db)
    highest = await bid_repo.get_highest_bid(body.auction_id)
    if highest and body.price <= highest.price:
        raise BidToLowError(f"Bid must exceed current highest: {highest.price}")
    return await bid_repo.create(
        user_id=current_user.id, auction_id=body.auction_id, price=body.price
    )
