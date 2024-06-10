from fastapi import FastAPI

from app.core import get_settings
from app.routes import init_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

init_router(app)
