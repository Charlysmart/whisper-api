from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.userSetting import UserSetting


class UserSettingCRUD:
    def __init__(self):
        pass

    async def get_user_setting(self, user: int, db: AsyncSession):
        stmt = await db.execute(select(UserSetting).where(UserSetting.user_id == user["id"]))
        result = stmt.scalar_one_or_none()
        if not result:
            post_preference = UserSetting(user_id = user)
            db.add(post_preference)
            try:
                await db.commit()
                await db.refresh(post_preference)
            except Exception as e:
                await db.rollback()
                return False
        return result
    
    async def update_preference(self, user: int, info: dict, db: AsyncSession):
        await db.execute(update(UserSetting).where(UserSetting.user_id == user["id"]).values(info))
        try:
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise False