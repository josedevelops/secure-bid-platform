# product type routes — CRUD endpoints for auction categories
# create is admin-only — we don't want random users polluting the category list
# list and get are public — buyers need to browse categories before placing bids
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.api.dependencies import get_current_user
from app.repository.product_type import ProductTypeRepository
from app.schemas.product_type import ProductTypeCreate, ProductTypeResponse
from app.db.models import User, MemberType
from app.core.errors import NotFoundError, AdminRequiredError

router = APIRouter(prefix="/product-types", tags=["product-types"])


@router.get("/", response_model=list[ProductTypeResponse])
async def list_product_types(db: AsyncSession = Depends(get_db)):
    # public endpoint — no auth required, anyone can browse categories
    repo = ProductTypeRepository(db)
    return await repo.get_all()


@router.get("/{product_type_id}", response_model=ProductTypeResponse)
async def get_product_type(
    product_type_id: int,
    db: AsyncSession = Depends(get_db),
):
    # public endpoint — fetch a single category by id
    repo = ProductTypeRepository(db)
    product_type = await repo.get_by_id(product_type_id)
    if not product_type:
        raise NotFoundError("Product type not found")
    return product_type


@router.post("/", response_model=ProductTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_product_type(
    body: ProductTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # admin-only — product types are platform-level data, not user-generated content
    if current_user.member_type != MemberType.ADMIN:
        raise AdminRequiredError()
    repo = ProductTypeRepository(db)
    return await repo.create(**body.model_dump())
