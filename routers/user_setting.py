from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, HTTPException, status
from schemas.user_setting import SettingIn
from services.user_setting import UserSettingCRUD
from utils.oauth import check_user_verified
from database.session import get_db

setting_router = APIRouter(prefix="/pages", tags=["Pages"])
userSettingCrud = UserSettingCRUD()

@setting_router.get("/user_setting")
async def get_user_setting(user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    result = await userSettingCrud.get_user_setting(user["id"], db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preference not found!")
    return {
        "user" : user["username"],
        "result": result
    }

@setting_router.patch("/update_preference")
async def update_preference(data: SettingIn, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    data_dict = data.model_dump()
    result = await userSettingCrud.get_user_setting(user["id"], db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preference not found!")
    
    updated = await userSettingCrud.update_preference(user["id"], data_dict, db)
    if updated:
        return { "message" : "Preference updated!" }
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't update preferences")