# product type repository — all database operations for product types live here
# we follow the same pattern as auction.py — one class, one responsibility
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import ProductType


class ProductTypeRepository:
    # we inject the db session here so the repository never manages its own connection
    # the route handler owns the session lifetime, not the repository
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str, description: str = None) -> ProductType:
        # build the model object — sqlalchemy tracks it as pending until we flush
        product_type = ProductType(name=name, description=description)

        # add to session — tells sqlalchemy to track this object for the next commit
        self.db.add(product_type)

        # flush sends the INSERT to the database but does not commit the transaction
        # this lets us read back the generated id before the transaction closes
        await self.db.flush()

        # refresh pulls the latest state from the database into our object
        # we need this to get the generated id, created_at, and updated_at timestamps
        await self.db.refresh(product_type)
        return product_type

    async def get_all(self) -> list[ProductType]:
        # select() builds a SELECT statement — scalars() unwraps the row tuples into objects
        result = await self.db.execute(select(ProductType).order_by(ProductType.name))
        return list(result.scalars().all())

    async def get_by_id(self, product_type_id: int) -> ProductType | None:
        # filter by primary key — returns None if not found, no exception raised
        result = await self.db.execute(
            select(ProductType).where(ProductType.id == product_type_id)
        )
        return result.scalar_one_or_none()
