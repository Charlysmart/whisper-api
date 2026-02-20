from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connect import SessionLocal
from models.whisperroom import Whisperroom
from schemas.whisperroom import FetchIn

class WhisperroomCRUD:
    def __init__(self):
        pass

    async def post_chat(self, **info):
        async with SessionLocal() as db:
            chat = Whisperroom(**info)
            db.add(chat)
            try:
                await db.commit()
                await db.refresh()
            except:
                await db.rollback()
                return False
            return chat
    
    async def get_chat(self, fetch: FetchIn, **info):
        async with SessionLocal() as db:
            stmt = select(Whisperroom)

            for field, value in info.items():
                column = getattr(Whisperroom, field, None)
                stmt = stmt.where(column == value)
            stmt = await db.execute(stmt)

            if fetch == "single":
                result = stmt.scalar_one_or_none()
            elif fetch == "all":
                result = stmt.scalars().all()
            
            return result
    
    async def delete_chat(self, message_id: int, user_id: int):
        async with SessionLocal() as db:
            await db.execute(delete(Whisperroom).where(Whisperroom.id == id, Whisperroom.sender_id == user_id))
            try:
                await db.commit()
            except:
                await db.rollback()
                return False
            return True