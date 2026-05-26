from app.db.base import Base
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.db.models import AuctionStatus


# used when creating a new auction
class AuctionCreate(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    detials: Optional[str] = None
    min_price: float = Field(gt=0)
    max_price: float = Field(gt=0)
    buyout_price: Optional[float] = None
    product_type_id: int


# used when updating an existing auction - all fields set to optional
# Optional on every field means the client only sends what changed
class AuctionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    details: Optional[str] = None
    min_price: Optional[float] = Field(None, gt=0)
    max_price: Optional[float] = Field(None, gt=0)
    buyout_price: Optional[float] = None
    status: Optional[AuctionStatus] = None


# Response sent back - includes fields like id and timestamp
class AuctionResponse(BaseModel):
    id: int
    name: str
    details: Optional[str]
    min_price: float
    max_price: float
    buyout_price: Optional[float]
    status: AuctionStatus
    user_id: int
    product_type_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
