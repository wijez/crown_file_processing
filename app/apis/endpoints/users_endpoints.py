from fastapi import status, Depends, APIRouter
from fastapi.security import HTTPAuthorizationCredentials

from app.core import get_settings, Config
from app.apis.depends import get_session
from app.apis.depends.check_auth import check_auth, check_user_permissions
from app.models import User
from app.services.users_service import UserService
from app.schemas import UserCreateSchema, UserUpdateSchema

logger = Config.setup_logging()

settings = get_settings()

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("")
async def create_user(request_body: UserCreateSchema, session: get_session,
                      user_decode: HTTPAuthorizationCredentials = Depends(check_auth),
                      user: User = Depends(check_user_permissions)):
    print("user", user_decode)
    logger.info("Endpoint: create_user called")
    user_service = UserService(session=session)
    result = await user_service.create_user(request_body)
    logger.info("Endpoint: create_user successfully!")
    return result


@router.put("/{user_id}")
async def update_user(request_body: UserUpdateSchema, user_id: int, session: get_session,
                      user_decode: HTTPAuthorizationCredentials = Depends(check_auth),
                      user: User = Depends(check_user_permissions)):
    logger.info("Endpoint: update_user called")
    user_service = UserService(session=session)
    result = await user_service.update_user(request_body, user_id)
    logger.info("Endpoint: update_user successfully!")
    return result


@router.get("")
async def get_list_user(session: get_session,
                        user_decode: HTTPAuthorizationCredentials = Depends(check_auth),
                        user: User = Depends(check_user_permissions),
                        limit: int = 10, offset: int = 0):
    logger.info("Endpoint: get_list_user called")
    user_service = UserService(session=session)
    result = await user_service.get_list_user(limit=limit, offset=offset)
    logger.info("Endpoint: get_list_user successfully!")
    return result


@router.delete("/{user_id}")
async def delete_user(user_id: int, session: get_session,
                      user_decode: HTTPAuthorizationCredentials = Depends(check_auth),
                      user: User = Depends(check_user_permissions)):
    logger.info("Endpoint: delete_user called")
    user_service = UserService(session=session)
    result = await user_service.delete_user(user_id)
    logger.info("Endpoint: delete_user successfully!")
    return result
