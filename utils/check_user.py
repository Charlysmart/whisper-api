from fastapi import Request, HTTPException, status
from utils.authentication_token import verify_token

def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code" : "TOKEN_EXPIRED",
                "message" : "Access token missing"
            }
        )

    user = verify_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code" : "TOKEN_EXPIRED",
                "message" : "Invalid or expired access token"
            }
        )

    return user