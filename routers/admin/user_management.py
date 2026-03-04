from typing import Literal
from fastapi import APIRouter, Depends
from database.session import get_db
from services.users import UserCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from utils.oauth import RoleChecker
from utils.time_extract import extract_time


user_management_router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])
UserCrud = UserCRUD()

@user_management_router.get("/user_management")
async def user_management(filter: Literal["verified", "unverified", "all"], page: int, order: Literal["desc", "asc"], admin: dict = Depends(RoleChecker("admin")), db: AsyncSession = Depends(get_db)):
    filter = True if filter == "verified" else False if filter == "unverified" else None
    if not filter:
        user = await UserCrud.get_all_users(db, page, order, None, **{"role" : "user"})
    else:
        user = await UserCrud.get_all_users(db, page, order, None, **{"role" : "user", "filter" : filter})
    if not user:
        return {
            "users" : [],
            "count" : 0
        }
    result = []
    for u in user["result"]:
        result.append({
            "username" : u.username,
            "anonymous_id" : u.custom_username,
            "verified" : u.verified,
            "joined_date" : extract_time(u.created_at)
        })
    return {    
        "users" : result,
        "count" : user["count"]
    }
        