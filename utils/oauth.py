from fastapi import Request, HTTPException, status, Depends
from utils.authentication_token import verify_token
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from model.users import AnonyUser

async def check_token(token: str, db: AsyncSession):
    user = verify_token(token)

    if not user:
        raise ValueError("Invalid or expired token")
    
    stmt = await db.execute(select(AnonyUser).where(AnonyUser.id == user["id"]))
    result = stmt.scalar_one_or_none()

    if not result:
        raise ValueError("User not found")

    if not result.verified:
        raise PermissionError("User not verified")
    
    return user


async def check_user_verified(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "TOKEN_EXPIRED",
                "message": "Access token missing"
            }
        )

    try:
        return await check_token(token, db)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "TOKEN_EXPIRED",
                "message": "Invalid or expired access token"
            }
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not verified"
        )