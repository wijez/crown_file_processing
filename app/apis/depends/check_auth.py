from fastapi import status, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils import verify_jwt, decode_token


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
