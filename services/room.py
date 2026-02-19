from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.join_room import JoinRoom
from models.room import Room
from schemas.room import FetchIn

class WhisperroomCRUD:
    def __init__(self):
        pass

    async def create_room(self, db: AsyncSession, **info):
        new_room = Room(**info)
        db.add(new_room)
        try:
            await db.commit()
            await db.refresh(new_room)
        except:
            await db.rollback()
            return False
        return new_room.room_thread
    
    async def join_room(self, db: AsyncSession, **info):
        stmt = JoinRoom(**info)
        db.add(stmt)
        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True
    
    async def select_joined_room(self, db: AsyncSession, fetch: FetchIn, **info):
        stmt = select(JoinRoom)

        for field, value in info.items():
            column = getattr(JoinRoom, field, None)
            stmt = stmt.where(column == value)
        stmt = await db.execute(stmt)

        if fetch == "single":
            result = stmt.scalar_one_or_none()
        elif fetch == "all":
            result = stmt.scalars().all()
        
        return result

    async def select_room(self, db: AsyncSession, fetch: FetchIn, **info):
        stmt = select(Room)

        for field, value in info.items():
            column = getattr(Room, field, None)
            stmt = stmt.where(column == value)
        stmt = await db.execute(stmt)

        if fetch == "single":
            result = stmt.scalar_one_or_none()
        elif fetch == "all":
            result = stmt.scalars().all()
        
        return result
    
    async def delete_room(self, db: AsyncSession, room_id: str, user_id):
        await db.execute(delete(Room).where(Room.room_thread == room_id, Room.admin == user_id))
        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True