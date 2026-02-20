from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from config.setting import Setting
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from services.store_token import TokenCRUD
from services.users import UserCRUD
from utils.authentication_token import create_access_token, create_refresh_token, verify_token
from utils.check_user import get_current_user
from utils.hash_token import hash_tokens
from utils.verification_token import generate_verification_token


verify_router = APIRouter(prefix="/auth", tags=["Authentication"])
setting = Setting()
tokenCrud = TokenCRUD()

# Verify email page
@verify_router.post("/verify_email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    result = await tokenCrud.get_tokens(db, token)

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect token! Kindly request for another token.")
    if result.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect token! Kindly request for another token.")
    elif result.expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired! Kindly request for another token.")
    elif result.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token already used! Kindly request for another token.")
    await tokenCrud.update_tokens(db, {"token": token})
    await UserCRUD().update_user(db, {"id" : result.user_id}, {"verified" : True})
    return {
        "message" : "Verification Successful!"
    }

# Resend Verification email
@verify_router.get("/resend_verification")
async def resend_verification(db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    token = generate_verification_token()
    send_token = await tokenCrud.store_tokens(token, "Email verification token", datetime.now(timezone.utc) + timedelta(minutes=5), user["id"], db)
    if not send_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error resending token! Kindly try again")
    return {
        "message" : "Code resent to your email!"
    }


# refresh token page
@verify_router.get("/refresh")
async def refresh_token(request: Request, response:Response, db: AsyncSession = Depends(get_db)):
    # get token from cookie
    token = request.cookies.get("refresh_token")
    
    # check if token exists in database
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing. Kindly re-login."
        )
    result = await tokenCrud.get_tokens(db, hash_tokens(token))

    # check if it exists in database or it is expired
    if (not result) or result.expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid refresh token!!! Kindly re-login.")
    
    # checks if the token has been revoked already
    if result.revoked:
        await tokenCrud.update_tokens(db, {"user_id" : result.user_id})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token! Kindly re-login.")
    
    # verify the token to be sure its correct
    verified = verify_token(token)

    # check if its still in use or the id matches that of the one in the database
    if verified == None or verified["id"] != result.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token!! Kindly re-login.")
    
    # create a new refresh and access token
    new_access_token = create_access_token({"id": verified["id"], "username" : verified["username"]})
    new_refresh_token = create_refresh_token({"id": verified["id"], "username" : verified["username"]})

    # update the database with the new refresh token and mark the old refresh token true
    await tokenCrud.update_tokens(db, {"token" : hash_tokens(token)})
    update_refresh = await tokenCrud.store_tokens(hash_tokens(new_refresh_token), "refresh token", datetime.now(timezone.utc) + timedelta(days=7), verified["id"], db)
    
    if not update_refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error refreshing token! Kindly re-login.")
    
    # set the cookies
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=setting.httponly,
        samesite=setting.samesite,
        secure=setting.secure,
        max_age= 7 * 24 * 60 * 60
    )
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=setting.httponly,
        samesite=setting.samesite,
        secure=setting.secure
    )
    return {
        "message": "Token refreshed successfully"
    }