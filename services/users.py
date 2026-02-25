from typing import Optional
from sqlalchemy import and_, column, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import Users
from schemas.users import FetchIn

class UserCRUD:
    def __init__(self):
        pass

    async def create_user(self, db: AsyncSession, **info):
        new_user = Users(**info)
        db.add(new_user)

        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True
    
    async def get_user(self, db: AsyncSession, fetch: FetchIn = "single", condition: Optional[str] = None, **info):
        stmt = select(Users)

        filters = []

        for field, value in info.items():
            column = getattr(Users, field, None)
            if column is not None:
                filters.append(column == value)

        if condition == "or":
            stmt = stmt.where(or_(*filters))
        else:
            stmt = stmt.where(and_(*filters))
            
        stmt = await db.execute(stmt)
        if fetch == "single":
            result = stmt.scalar_one_or_none()
        elif fetch == "all":
            result = stmt.scalars().all()
        else:
            return None
        
        return result if result else False
    
    async def update_user(self, db: AsyncSession, where: dict, info: dict):
        stmt = update(Users)

        for field, value in where.items():
            column = getattr(Users, field, None)
            if not column:
                continue
            stmt = stmt.where(column == value)
            
        stmt = await db.execute(stmt.values(info))
        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True