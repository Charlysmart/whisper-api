from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, or_, select, update
from config.setting import Setting
from database.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from models.tokens import Tokens
from schemas.users import AdminRegister, LoginInfo, RegisterUserIn
from sqlalchemy.ext.asyncio import AsyncSession
from services.send_mail import SendEmail
from services.store_token import TokenCRUD
from services.users import UserCRUD
from utils.hash_password import hash_password, verify_password
from utils.authentication_token import create_access_token, create_refresh_token
from utils.check_user import get_current_user
from utils.hash_token import hash_tokens
from utils.username import create_username
from utils.verification_token import generate_verification_token


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
setting = Setting()
userCrud = UserCRUD()
tokenCrud = TokenCRUD()
emailSend = SendEmail()

@auth_router.post("/signup")
async def sign_up(user: RegisterUserIn, db: AsyncSession = Depends(get_db)):
    userInfo = user.model_dump()
    checked_user = await userCrud.get_user(db, "or", **{"username" : userInfo["username"], "email" : userInfo["email"]})

    # check if the user exists in the database already
    if checked_user:
        if checked_user.username == user.username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists!")
        elif checked_user.email == user.email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists!")
        
    custom_username:str 
    
    # generate the site username and makes sure it doesn't exist in the database
    while True:
        custom_username = create_username()
        check_user = await userCrud.get_user(db, None, **{"custom_username" : custom_username})
        if not check_user:
            break
            
    userInfo["custom_username"] = custom_username
    userInfo["password"] = hash_password(userInfo["password"])
    del userInfo["confirm_password"]
    new_user = await userCrud.create_user(db, **userInfo)
    if not new_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating an account! Kindly try again shortly.")
    return {
        "message": "Account created successfully! Kindly login to verify your email."
    }


# Login page
@auth_router.post("/login")
async def login(user: LoginInfo, response: Response, db: AsyncSession = Depends(get_db)):
    result = await userCrud.get_user(db, None, **{"username" : user.username})

    if not result:
        raise HTTPException(status_code=401, detail="User not found!")
    
    if not verify_password(result.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Password!")
    
    access_token = create_access_token({"id": result.id, "username": result.username, "role": result.role})
    refresh_token = create_refresh_token({"id": result.id, "username": result.username, "role": result.role})
    store_refresh_token = await tokenCrud.store_tokens(hash_tokens(refresh_token), "refresh token", datetime.now(timezone.utc) + timedelta(days=7), result.id, db)
    if not store_refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error while logging in! Kindly try again shortly.")
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=setting.httponly,
        samesite=setting.samesite,
        secure=setting.secure,
        max_age=7*24*60*60
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=setting.httponly,
        samesite=setting.samesite,
        secure=setting.secure
    )

    if not result.verified:
        # Delete old tokens for this reason first
        deleted = await tokenCrud.delete_tokens(db, **{"user_id": result.id, "reason": "Email verification token"})
        if deleted is False:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while logging in!!! Kindly try again shortly.")

        # Generate new verification token
        verification_token = generate_verification_token()

        # Store token in DB with expiry
        store_verification_token = await tokenCrud.store_tokens(
            verification_token,
            "Email verification token",
            datetime.now(timezone.utc) + timedelta(minutes=10),
            result.id,
            db
        )
        if store_verification_token is False:
            raise HTTPException(status_code=500, detail="Error storing verification token.")

        # Send email
        email_sender = emailSend.send_verification_email(result.email, result.username, verification_token)
        if email_sender is False:
            raise HTTPException(status_code=500, detail="Error sending email.")

        return {"message": "Verification sent to email! Kindly check your email for your token."}

    return {"message": "Login Successful!"}


@auth_router.post("/admin_signup")
async def adminSignup(info: AdminRegister, db: AsyncSession = Depends(get_db)):
    userInfo = info.model_dump()
    checked_user = await userCrud.get_user(db, "or", **{"username" : userInfo["username"]})

    # check if the user exists in the database already
    if checked_user:
        if checked_user.username == info.username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists!")
        
    custom_username:str 
    
    # generate the site username and makes sure it doesn't exist in the database
    while True:
        custom_username = create_username()
        check_user = await userCrud.get_user(db, None, **{"custom_username" : custom_username})
        if not check_user:
            break
            
    userInfo["custom_username"] = custom_username
    userInfo["password"] = hash_password(userInfo["password"])
    new_user = await userCrud.create_user(db, **userInfo)
    if not new_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating an account! Kindly try again shortly.")
    return {
        "message": "Account created successfully! Kindly login to verify your email."
    }


@auth_router.delete("/logout")
async def logout(response: Response, request: Request, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    await tokenCrud.delete_tokens(db, **{"token" : token})
    try:
        await db.commit()
        response.delete_cookie(
            key="access_token",
            httponly=False,
            samesite="none",
            secure=True
        )
        response.delete_cookie(
            key="refresh_token",
            httponly=False,
            samesite="none",
            secure=True
        )
    except:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to logout")
    return {
        "message" : "Logged out!"
    }