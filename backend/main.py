from fastapi import FastAPI

from backend.api.routes.review import router as review_router
from backend.core.logger import logger
from backend.core.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered GitHub Pull Request Review Bot",
    version=settings.APP_VERSION,
)


@app.on_event("startup")
async def startup_event():
    logger.info("Application started successfully.")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")

    return {
        "status": "success",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
    }


from backend.core.constants import API_PREFIX

app.include_router(
    review_router,
    prefix=API_PREFIX,
    tags=["Code Review"],
)