from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, or_, select, update
from config.setting import Setting
from database.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from models.tokens import Tokens
from schemas.users import LoginInfo, RegisterUserIn
from sqlalchemy.ext.asyncio import AsyncSession
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

@auth_router.post("/signup")
async def sign_up(user: RegisterUserIn, db: AsyncSession = Depends(get_db)):
    userInfo = user.model_dump()
    checked_user = await userCrud.get_user(db, "single", "or", **{"username" : userInfo["username"], "email" : userInfo["email"]})

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
        check_user = await userCrud.get_user(db, "single", None, **{"custom_username" : custom_username})
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
    result = await userCrud.get_user(db, "single", None, **{"username" : user.username})

    if not result:
        raise HTTPException(status_code=401, detail="User not found!")
    
    if not verify_password(result.password, user.password):
        print(f"in: {result.password} out: {user.password}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Password!")
    
    access_token = create_access_token({"id": result.id, "username": result.username})
    refresh_token = create_refresh_token({"id": result.id, "username": result.username})
    store_refresh_token = await tokenCrud.store_tokens(hash_tokens(refresh_token), "refresh token", datetime.now(timezone.utc) + timedelta(days=7), result.id, db)
    if not store_refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error while logging in! Kindly try again shortly.")
    print(refresh_token, access_token)
    
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
        updated = await tokenCrud.update_tokens(db, **{"user_id" : result.id, "reason" : "Email verification token", "revoked" : False})
        if not updated:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while logging in!!! Kindly try again shortly.")
        deleted = await tokenCrud.delete_tokens(db, **{"user_id" : result.id, "reason" : "Email verification token"})
        if not deleted:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while logging in!! Kindly try again shortly.")
        verification_token = generate_verification_token()
        store_verification_token = await tokenCrud.store_tokens(verification_token, "Email verification token", datetime.now(timezone.utc) + timedelta(minutes=5), result.id, db)
        if not store_verification_token:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while logging in! Kindly try again shortly.")
        return {
            "message" : "Verification sent to email! Kindly check your email for your token"
        }
    return {
        "message" : "Login Successful!"
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