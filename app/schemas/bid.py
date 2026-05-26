# schemas for bid request and response shapes
from pydantic import BaseModel, Field
from datetime import datetime


# used when placing a new bid
# only needs price and auction reference
class BidCreate(BaseModel):
    auction_id: int
    price: float = Field(gt=0)  # < must be greater than zero


# what is sent back after a bid is placed
class BidResponse(BaseModel):
    id: int
    price: float
    auction_id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
