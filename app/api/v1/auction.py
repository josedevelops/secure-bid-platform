# auction routes — create, read, update, close
# we use custom exceptions from errors.py so all error responses
# have consistent JSON shape across the entire API
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.api.dependencies import get_current_user
from app.repository.auction import AuctionRepository
from app.schemas.auction import AuctionCreate, AuctionUpdate, AuctionResponse
from app.db.models import User, MemberType
from app.core.errors import NotFoundError, ForbiddenError, SellerRequiredError

router = APIRouter(prefix="/auctions", tags=["auctions"])


@router.get("/", response_model=list[AuctionResponse])
async def list_auctions(db: AsyncSession = Depends(get_db)):
    # public endpoint — no auth required to browse auctions
    repo = AuctionRepository(db)
    return await repo.get_all_active()


@router.get("/{auction_id}", response_model=AuctionResponse)
async def get_auction(auction_id: int, db: AsyncSession = Depends(get_db)):
    repo = AuctionRepository(db)
    auction = await repo.get_by_id(auction_id)
    if not auction:
        raise NotFoundError("Auction not found")
    return auction


@router.post("/", response_model=AuctionResponse, status_code=status.HTTP_201_CREATED)
async def create_auction(
    body: AuctionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # only sellers can create auctions — buyers browse and bid
    if current_user.member_type not in [MemberType.SELLER, MemberType.ADMIN]:
        raise SellerRequiredError()
    repo = AuctionRepository(db)
    return await repo.create(user_id=current_user.id, **body.model_dump())


@router.patch("/{auction_id}", response_model=AuctionResponse)
async def update_auction(
    auction_id: int,
    body: AuctionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = AuctionRepository(db)
    auction = await repo.get_by_id(auction_id)
    if not auction:
        raise NotFoundError("Auction not found")
    # only the owner or admin can update
    if auction.user_id != current_user.id and current_user.member_type != MemberType.ADMIN:
        raise ForbiddenError()
    # exclude_none=True means only send fields the client actually provided
    return await repo.update(auction, **body.model_dump(exclude_none=True))


@router.post("/{auction_id}/close", response_model=AuctionResponse)
async def close_auction(
    auction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = AuctionRepository(db)
    auction = await repo.get_by_id(auction_id)
    if not auction:
        raise NotFoundError("Auction not found")
    if auction.user_id != current_user.id and current_user.member_type != MemberType.ADMIN:
        raise ForbiddenError()
    return await repo.close(auction)
