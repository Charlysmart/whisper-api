from services.users import UserCRUD
from utils.oauth import check_user_verified
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db

general_router = APIRouter(prefix="/pages", tags=["Pages"])
userCrud = UserCRUD()

@general_router.get("/general")
async def general(user: dict = Depends(check_user_verified)):
    if user:
        return True
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in")


@general_router.get("/health")
def health():
    return {"status": "ok"}




@general_router.get("/user")
async def general(user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    result = await userCrud.get_user(db, "single", None, {"id" : user["id"]})
    return {
        "username" : result.custom_username,
        "whisper_username" : result.anony_username
    }