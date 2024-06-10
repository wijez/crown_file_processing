from fastapi import Request, Response, status, Depends, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_settings
from app.services import AuthService
from app.apis.depends import get_session

from app.schemas import ResponseSchema, UserCreateSchema, UserLoginSchema, UserVerifyCodeSchema

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ResponseSchema)
async def register(request_body: UserCreateSchema, session: get_session):
    result = await AuthService.register(schema=request_body, session=session)
    return ResponseSchema(status_code=status.HTTP_200_OK, detail='Register successfully', result=result)


@router.post("/verify-code", response_model=ResponseSchema)
async def verify_code(request_body: UserVerifyCodeSchema, session: get_session):
    await AuthService.verify_code(schema=request_body, session=session)
    return ResponseSchema(status_code=status.HTTP_200_OK, detail='Verify code successfully')


@router.post("/login", response_model=ResponseSchema)
async def login(request_body: UserLoginSchema, session: get_session):
    result = await AuthService.login(schema=request_body, session=session)
    return ResponseSchema(status_code=status.HTTP_200_OK, detail='Login successfully', result=result)


@router.get("/refresh-token", response_model=ResponseSchema)
async def refresh_token(session: get_session,
                        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=True))):
    result = await AuthService.refresh_token(session=session, credentials=credentials)
    return ResponseSchema(status_code=status.HTTP_200_OK, detail='Refresh token successfully', result=result)

    # @router.get("/logout", response_model=ResponseSchema)
    # async def logout(response: Response, user_decode: HTTPAuthorizationCredentials = Depends(check_auth),
    #                  session: AsyncSession = Depends(get_session)):
    #     await AuthService.logout(response=response, user_decode=user_decode, session=session)
    #     return ResponseSchema(status_code=status.HTTP_200_OK, detail="Đăng xuất thành công")
