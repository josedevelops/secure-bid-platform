# main.py is the entry point - creates the FastAPI app and wires all routers together

from app.api.v1 import profile
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.metrics import setup_metrics
from app.api.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.auction import router as auction_router
from app.api.v1.bid import router as bid_router
from app.api.v1.profile import router as profile_router
from app.api.v1.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs once on startup before any requests are handled
    setup_logging()
    yield
    # anything after yield runs on shutdown


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        # disable docs in production
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # CORS - control which frontend origins can call this API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # register all routers with the /api/v1 prefix
    app.include_router(health_router)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(auction_router, prefix="/api/v1")
    app.include_router(bid_router, prefix="/api/v1")
    app.include_router(profile_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/api/v1")

    # attach prometheus metrics endpoints
    setup_metrics(app)

    return app


app = create_app()
