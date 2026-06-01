# conftest.py — shared test fixtures for the entire test suite
# pytest automatically loads this file before any test runs
# fixtures defined here are available to all test files without importing

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.db.base import Base, get_db

# host is 'db' because inside Docker, services talk by service name not localhost
TEST_DATABASE_URL = "postgresql+asyncpg://appuser:changeme@db:5432/securebid_test"


@pytest_asyncio.fixture
async def db_session():
    # we create the engine INSIDE the fixture so it uses the current event loop
    # creating it at module level causes "Future attached to a different loop" errors
    # because each test gets a fresh event loop but the engine holds connections
    # from the previous loop
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # create all tables fresh for this test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # provide a session to the test
    async with session_factory() as session:
        yield session
        await session.rollback()

    # drop all tables after the test — clean slate for next test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # dispose the engine — closes all connections cleanly
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    # provides an httpx AsyncClient wired to the FastAPI app
    # we override get_db so every request uses the test session
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    # clear the override after each test
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def buyer_token(client):
    # creates a buyer user and returns a valid JWT token
    await client.post("/api/v1/auth/signup", json={
        "username": "testbuyer",
        "email": "testbuyer@test.com",
        "password": "Testpass1!"
    })
    response = await client.post("/api/v1/auth/login", json={
        "username": "testbuyer",
        "password": "Testpass1!"
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def seller_token(client, db_session):
    # creates a seller user, promotes to SELLER in db, returns token
    from app.repository.user import UserRepository
    from app.db.models import MemberType

    await client.post("/api/v1/auth/signup", json={
        "username": "testseller",
        "email": "testseller@test.com",
        "password": "Testpass1!"
    })
    repo = UserRepository(db_session)
    user = await repo.get_by_username("testseller")
    user.member_type = MemberType.SELLER
    await db_session.commit()

    response = await client.post("/api/v1/auth/login", json={
        "username": "testseller",
        "password": "Testpass1!"
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def admin_token(client, db_session):
    # creates an admin user, promotes to ADMIN in db, returns token
    from app.repository.user import UserRepository
    from app.db.models import MemberType

    await client.post("/api/v1/auth/signup", json={
        "username": "testadmin",
        "email": "testadmin@test.com",
        "password": "Testpass1!"
    })
    repo = UserRepository(db_session)
    user = await repo.get_by_username("testadmin")
    user.member_type = MemberType.ADMIN
    await db_session.commit()

    response = await client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "Testpass1!"
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def product_type(client, admin_token):
    # creates a product type and returns it — used by auction tests
    response = await client.post(
        "/api/v1/product-types/",
        json={"name": "Electronics", "description": "Electronic devices"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return response.json()
