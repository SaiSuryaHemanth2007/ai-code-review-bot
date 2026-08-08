from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes.github import router as github_router
from backend.api.routes.review import router as review_router
from backend.api.routes.history import router as history_router
from backend.api.routes.dashboard import router as dashboard_router
from backend.api.routes.webhooks import router as webhook_router
from backend.api.routes.health import router as health_router
from backend.api.routes.metrics import router as metrics_router
from backend.core.constants import API_PREFIX
from backend.core.logger import logger
from backend.core.settings import settings
from backend.core.exception_handler import (
    register_exception_handlers,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started successfully.")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered GitHub Pull Request Review Bot",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

register_exception_handlers(app)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")

    return {
        "status": "success",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
    }


# ----------------------------
# Review Routes
# ----------------------------

app.include_router(
    review_router,
    prefix=API_PREFIX,
    tags=["Code Review"],
)


# ----------------------------
# GitHub Routes
# ----------------------------

app.include_router(
    github_router,
    prefix=f"{API_PREFIX}/github",
    tags=["GitHub"],
)


# ----------------------------
# History Routes
# ----------------------------

app.include_router(
    history_router,
    prefix=API_PREFIX,
    tags=["Review History"],
)


# ----------------------------
# Dashboard Routes
# ----------------------------

app.include_router(
    dashboard_router,
    prefix=API_PREFIX,
    tags=["Dashboard"],
)


app.include_router(
    webhook_router,
    prefix=API_PREFIX,
    tags=["Webhooks"],
)


app.include_router(
    health_router,
    prefix="/api/v1",
    tags=["Health"],
)


app.include_router(
    metrics_router,
    prefix="/api/v1",
    tags=["Metrics"],
)