from datetime import datetime, timedelta
from typing import List, Union
from fastapi import status, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.apis.depends import get_db_session, get_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.utils import verify_jwt, decode_token
from app.opa.permissions.base_permissions import OpenPolicyAgentPermission
from app.services import UserService
from app.core.settings import get_settings

from app.utils.misc import create_bullet_list
from app.core import Config

settings = get_settings()
logger = Config.setup_logging()


def check_auth(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=True))):
    if credentials:
        if not credentials.scheme == "Bearer":
            # Return Forbidden if the authentication scheme is not Bearer
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"status": "Forbidden", "message": "Invalid token!"}
            )
        if not verify_jwt(token=credentials.credentials):
            # Return Forbidden if the token is invalid or expired
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"status": "Forbidden", "message": "Token is invalid or expired!"}
            )
        return decode_token(token=credentials.credentials)
    else:
        # Return Forbidden if there are no valid credentials
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": "Forbidden", "message": "Lỗi hệ thống!"}
        )


async def verify_token(token: str, session: AsyncSession):
    if not token:
        logger.error(f'Error Invalid Token.',
                     exc_info=ValueError(status.HTTP_400_BAD_REQUEST))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid token"
        )

    try:
        decoded_token = jwt.decode(token,
                                   settings.JWT_SECRET,
                                   algorithms=settings.ALGORITHM)
    except jwt.exceptions.ExpiredSignatureError:
        logger.error(f'Error Expired Token.',
                     exc_info=ValueError(status.ERROR_401_EXPIRED_TOKEN))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="expired token")

    # check user existence
    user_id = decoded_token['user_id']
    user_service = UserService(session=session)
    await user_service.get_one_by_id(user_id=user_id)

    return decoded_token


async def get_current_active_user(
        request: Request,
        session: get_session,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
):
    token = None
    if request.cookies.get("access_token", None):
        token = request.cookies["access_token"]
    elif credentials:
        token = credentials.credentials
    user_decode = await verify_token(token=token, session=session)
    user_id = user_decode['user_id']
    user_service = UserService(session=session)
    user = await user_service.get_one_by_id(user_id=user_id)

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


async def gather_permissions(request: Request, user: User, session: AsyncSession) -> List[OpenPolicyAgentPermission]:
    permissions = []
    for perm_class in OpenPolicyAgentPermission.__subclasses__():
        permissions.extend(await perm_class.create(request=request, user=user, session=session))
    return permissions


async def check_permissions(permissions: List[OpenPolicyAgentPermission]):
    allow = True
    reasons = []

    for perm in permissions:
        result = await perm.check_access()
        reasons.extend(result.reasons)
        allow &= result.allow
    if not allow:
        if len(reasons):
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                detail=create_bullet_list(reasons))
        else:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
    return allow


async def filter_by_user_permissions(request: Request,
                                     session: get_session,
                                     user: User = Depends(get_current_active_user)
                                     ) -> List[Union[dict, str]]:
    user_permissions = await gather_permissions(request=request, user=user, session=session)

    filter_rpn = []

    for perm in user_permissions:
        if perm.payload['input']['scope'] == 'list':
            result = await perm.filter()
            if len(filter_rpn):
                filter_rpn.extend(result.filter_rpn.extend(['&']))
            else:
                filter_rpn.extend(result.filter_rpn)

    return filter_rpn


async def check_user_permissions(request: Request, session: get_session,
                                 user: User = Depends(get_current_active_user)):
    user.id = str(user.id)
    user_permissions = await gather_permissions(request=request, session=session, user=user)
    await check_permissions(user_permissions)
    return user
