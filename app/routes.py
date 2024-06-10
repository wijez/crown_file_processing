from fastapi import FastAPI, APIRouter

from app.apis.endpoints import auth_router, users_router
from app.core import get_settings

settings = get_settings()


def init_router(app: FastAPI):
    main_router = APIRouter(prefix=settings.BASE_API_SLUG)

    main_router.include_router(auth_router)
    main_router.include_router(users_router)

    app.include_router(main_router)

