# schemas for user profile request and response shapes
from app.db.base import Base
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from app.db.models import MemberType


# used when updating a profile - all fields optional
class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    member_type: Optional[MemberType] = None


# used when changing password - will require current password for verification
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


# what is sent back
class ProfileResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    member_type: MemberType
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
