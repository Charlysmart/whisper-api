from typing import Literal, Optional
from sqlalchemy import and_, asc, column, desc, func, or_, select, update
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
    
    async def get_all_users(self, db: AsyncSession, page: int, order: Literal["desc", "asc"], condition: Optional[str] = None, **info):
        stmt = select(Users)
        get_count = select(func.count()).select_from(Users)

        limit = 20
        skip = (page - 1) * limit
        order = desc if order == "desc" else asc
        filters = []

        for field, value in info.items():
            column = getattr(Users, field, None)
            if column is not None:
                filters.append(column == value)

        if condition == "or":
            stmt = stmt.where(or_(*filters))
            get_count = get_count.where(or_(*filters))
        else:
            stmt = stmt.where(and_(*filters))
            get_count = get_count.where(and_(*filters))
            
        stmt = await db.execute(stmt.order_by(order(Users.created_at)).offset(skip).limit(limit))
        get_count = await db.execute(get_count)
        result = stmt.scalars().all()
        count = get_count.scalar_one()
        
        if not result:
            return None
        return {
            "result" : result,
            "count" : count
        }
    
    async def get_all_specified_users(self, db: AsyncSession, limit: int, order: Literal["desc", "asc"], condition: Optional[str] = None, **info):
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
            
        order_func = desc if order == "desc" else asc
        stmt = await db.execute(stmt.order_by(order_func(Users.created_at)).limit(limit))
        result = stmt.scalars().all()
        
        if not result:
            return None
        return {
            "result" : result
        }
    
    async def get_user(self, db: AsyncSession, condition: Optional[str] = None, **info):
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
        result = stmt.scalar_one_or_none()
        
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