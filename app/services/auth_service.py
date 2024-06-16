from typing import Annotated

from fastapi import Request, Response, HTTPException, status, Header
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core import get_settings
from app.crud import crud_user
from app.schemas import UserCreateSchema, UserLoginSchema, UserVerifyCodeSchema
from app.utils import (verify_password, hash_password, create_access_token, decode_token,
                       clear_refresh_token, send_email, generate_verify_code, create_refresh_token)

settings = get_settings()


class AuthService:
    @staticmethod
    async def register(schema: UserCreateSchema, session: AsyncSession):
        user = await crud_user.find_one_by_username(username=schema.username, session=session)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Username is already taken!')

        schema.password = hash_password(password=schema.password)

        verify_code = generate_verify_code()
        schema.verify_code = verify_code

        created_user = await crud_user.create_one(schema=schema, session=session)

        access_token = create_access_token(user=created_user)
        refresh_token = create_refresh_token(user=created_user)

        await send_email(to=created_user.email, subject="Verify account", contents=verify_code)
        result = {
            "data": created_user.dict(un_selects=["password"]),
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return result

    @staticmethod
    async def verify_code(schema: UserVerifyCodeSchema, session: AsyncSession):
        user = await crud_user.find_one_by_email(email=schema.email, session=session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='User not found!')

        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='User is already active!')

        if user.verify_code != schema.verify_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Verify code is not correct!')

        await crud_user.update(session=session, db_obj=user, obj_in={"is_active": True})

        return {
            "message": "Verify code successfully!"
        }

    @staticmethod
    async def login(schema: UserLoginSchema, session: AsyncSession):
        user = await crud_user.find_one_by_username(username=schema.username, session=session)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active!")

        if not verify_password(schema.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized!")

        # generate token
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        return {
            "data": user.dict(un_selects=["password"]),
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    @staticmethod
    async def refresh_token(authorization: Annotated[str, Header()], session: AsyncSession,
                            credentials: HTTPAuthorizationCredentials):
        print(authorization)
        if not credentials:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Missing token!')
        print(credentials.credentials)
        try:
            user_decode = decode_token(token=credentials.credentials)
            user = await crud_user.find_one_by_id(id=int(user_decode['user_id']), session=session)

            if not user:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized!')

            access_token = create_access_token(user=user)
            refresh_token = create_refresh_token(user=user)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        except Exception:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden!")

    @staticmethod
    async def logout(response: Response, user_decode: dict, session: AsyncSession):
        # check username
        user = await crud_user.find_one_by_id(id=user_decode.get('user_id'), session=session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Người dùng không tồn tại!")

        await crud_user.update_token_version(id=user.id, token_version=user.token_version + 1, session=session)
        clear_refresh_token(response=response)
