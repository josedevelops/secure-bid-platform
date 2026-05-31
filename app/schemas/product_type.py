# product_type schemas — defines what data comes in and what goes out
# we follow the same Create/Response pattern used in auction.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# we use ProductTypeCreate for POST /api/v1/product-types/
# Field(min_length=...) enforces validation before it ever hits the database
class ProductTypeCreate(BaseModel):
    # name is required — what kind of item is being auctioned (e.g. Electronics, Vehicles)
    name: str = Field(min_length=2, max_length=100)
    # description is optional — extra context about the category
    description: Optional[str] = None


# ProductTypeResponse is what we send back to the client
# includes id and timestamps that the database generates — client never sends these
class ProductTypeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    # from_attributes=True tells pydantic to read from SQLAlchemy model attributes
    # without this, pydantic can't convert a db row object into this schema
    model_config = {"from_attributes": True}
