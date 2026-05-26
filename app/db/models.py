import uuid
from datetime import datetime, timezone

from sqlalchemy.sql.traversals import _flatten_clauseelement
from app.db.base import Base
import enum
from sqlalchemy.orm import Mapped, immediateload, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, Float, Text, DateTime, ForeignKey, Enum


class MemberType(str, enum.Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class AuctionStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    SOLD = "sold"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    member_type: Mapped[MemberType] = mapped_column(
        Enum(MemberType), nullable=False, default=MemberType.BUYER
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    auctions: Mapped[list["Auction"]] = relationship("Auction", back_populates="user")
    bids: Mapped[list["Bid"]] = relationship("Bid", back_populates="user")


class ProductType(Base):
    __tablename__ = "product_types"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    auctions: Mapped[list["Auction"]] = relationship(
        "Auction", back_populates="product_types"
    )


class Auction(Base):
    __tablename__ = "auctions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    min_price: Mapped[float] = mapped_column(Float, nullable=False)
    max_price: Mapped[float] = mapped_column(Float, nullable=False)
    buyer_price: Mapped[float] = mapped_column(
        Enum(AuctionStatus), nullable=False, default=AuctionStatus.ACTIVE
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_id"),
        nullable=False,
    )
    producty_type_id: Mapped[int] = mapped_column(
        ForeignKey("producty_type_id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    update_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    user: Mapped["User"] = relationship("User", back_populates="auctions")
    product_type: Mapped["ProductType"] = relationship(
        "ProductType", back_populates="auctions"
    )
    bids: Mapped[list["Bids"]] = relationship("Bid", back_populates="auction")
    sold: Mapped["Sold"] = relationship(
        "Sold",
        back_populates="auction",
        uselist=False,
    )


class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    auction_id: Mapped[int] = mapped_column(ForeignKey("auctions.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    auction: Mapped["Auction"] = relationship("Auction", back_populates="bids")
    user: Mapped["User"] = relationship("User", back_populates="bids")
    sold: Mapped["Sold"] = relationship("Sold", back_populates="bid", uselist=False)


class Sold(Base):
    __tablename__ = "sold"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bid_id: Mapped[int] = mapped_column(
        ForeignKey("bids.id"),
        nullable=False,
        unique=True,
    )
    auction_id: Mapped[int] = mapped_column(
        ForeignKey("auctions.id"),
        nullable=False,
        unique=True,
    )
    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    sold_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # relationship to navigate from a sale back to the bid, auction and buyer
    bid: Mapped["Bid"] = relationship(
        "Bid",
        back_populates="sold",
    )
    auction: Mapped["Auction"] = relationship(
        "Auction",
        back_populates="sold",
    )
