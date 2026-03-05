from typing import Literal
from services.users import UserCRUD
from utils.oauth import RoleChecker, check_user_verified
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db

general_router = APIRouter(prefix="/pages", tags=["Pages"])
userCrud = UserCRUD()

@general_router.get("/general")
async def general(user: dict = Depends(check_user_verified)):
    return True

@general_router.get("/protected_route")
async def general(user: dict = Depends(RoleChecker())):
    return True


@general_router.get("/health")
def health():
    return {"status": "ok"}


@general_router.get("/user")
async def general(user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    result = await userCrud.get_user(db, None, **{"id" : user["id"]})
    return {
        "username" : result.username,
        "custom_username" : result.custom_username,
        "role" : result.role
    }