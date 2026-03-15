from database.session import get_db
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from routers.admin.user_management import UserCrud
from schemas.reset_password import ResetPassword
from services.send_mail import SendEmail
from services.store_token import TokenCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from utils.hash_password import hash_password
from utils.verification_token import generate_verification_token

reset_password_router = APIRouter(prefix="/auth", tags=["Authentication"])

emailSender = SendEmail()
tokenCrud = TokenCRUD()

@reset_password_router.get("/get_username")
async def forgot_password(username: str, db: AsyncSession = Depends(get_db)):
    username = username.lower()
    check_user = await UserCrud.get_user(db, None, username=username)
    if not check_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username not found")
    token = generate_verification_token()
    store_code = await tokenCrud.store_tokens(token, "password reset", datetime.now(timezone.utc) + timedelta(minutes=10), check_user.id, db)
    if not store_code:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate reset link at the moment. Kindly try again later")
    send_code = emailSender.send_reset_email(check_user.email, username, token)

    if not send_code:
        raise HTTPException(status_code=500, detail="Error sending OTP.")
    return {
        "message" : f"OTP has been sent to your email!{check_user.id}"
    }
    
@reset_password_router.get("check_otp")
async def check_otp(token: str, db: AsyncSession = Depends(get_db)):
    check_token = await tokenCrud.get_tokens(db, token)
    if not check_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect OTP")
    if check_token.revoked:
        raise HTTPException(status_code=status.HTTP_401_NOT_FOUND, detail="OTP already used")
    if datetime.now(timezone.utc) > check_token.expiry:
        raise HTTPException(status_code=status.HTTP_401, detail="OTP expired")
    return True

@reset_password_router.post("reset_password")
async def reset_password(info: ResetPassword, token: str, db: AsyncSession = Depends(get_db)):
    check_token = await tokenCrud.get_tokens(db, token)
    if not check_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect OTP")
    if check_token.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP already used")
    if datetime.now(timezone.utc) > check_token.expiry:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP expired")
    
    values = {
        "id" : check_token.user_id
    }

    updated_value = await UserCrud.update_user(db=db, where=values, password=hash_password(info.password))

    if not updated_value:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password")
    await tokenCrud.delete_tokens(db, token=token)
    return {
        "message" : "Password resetted successfully"
    }