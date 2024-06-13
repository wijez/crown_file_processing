from typing import Optional
from datetime import timedelta, datetime

from jose import jwt
from fastapi import Response

from app.models import User
from app.core import get_settings

settings = get_settings()


def generate_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # Prepare the data to be encoded in the JWT
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"iat": datetime.utcnow()})
    to_encode.update({"exp": expire})

    # Generate and return the JWT token
    encode_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return encode_jwt


# def generate_token(data: dict, expires_delta: Optional[timedelta] = None, token_type: str = None) -> str:
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#
#     to_encode.update({"iat": datetime.utcnow(), "exp": expire})
#     if token_type:
#         to_encode.update({"token_type": token_type})
#
#     encode_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
#     return encode_jwt


def decode_token(token: str) -> dict:
    try:
        # Attempt to decode the token, and check for expiration
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return decoded_token if datetime.utcfromtimestamp(decoded_token["exp"]) >= datetime.utcnow() else None
    except jwt.ExpiredSignatureError:
        # Handle expired token
        return None
    except jwt.JWTError:
        # Handle other JWT errors
        return {}


def verify_jwt(token: str):
    # Verify the JWT token
    try:
        user_decode = decode_token(token=token)
        return True if user_decode else False
    except jwt.ExpiredSignatureError:
        # Handle expired token
        return False
    except jwt.JWTError:
        # Handle other JWT errors
        return False


def create_access_token(user: User):
    return (generate_token(data={"user_id": user.id, "username": user.username},
                           expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)))


def create_refresh_token(user: User):
    return (generate_token(data={"user_id": user.id, "username": user.username},
                           expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_HOURS)))


def clear_refresh_token(response: Response):
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="lax",
        path=f"{settings.BASE_API_SLUG}/auth/refresh-token"
    )

# def create_token(data: dict, token_type: str, expires_delta: timedelta):
#     to_encode = data.copy()
#     to_encode.update({"token_type": token_type, "exp": datetime.utcnow() + expires_delta})
#     encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
#     return encoded_jwt
#
#
# def create_access_token(user: User):
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     data = {"user_id": user.id, "username": user.username}
#     return generate_token(data, expires_delta=access_token_expires, token_type="access")
#
#
# def create_refresh_token(user: User):
#     refresh_token_expires = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
#     data = {"user_id": user.id, "username": user.username}
#     return generate_token(data, expires_delta=refresh_token_expires, token_type="refresh")
