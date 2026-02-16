from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.chat import Chat

class InboxCRUD:
    def __init__(self):
        pass

    async def send_chat(self, db: AsyncSession, **info):
        chat = Chat(**info)
        db.add(chat)

        try:
            await db.commit()
            await db.refresh()
        except:
            await db.rollback()
            return False
        return chat
    
    async def get_chat(self, db: AsyncSession, **info):
        stmt = select(Chat)
        
        for field, value in info.items():
            column = getattr(Chat, field, None)

            if not column:
                continue
            stmt = stmt.where(column == value)
        stmt = await db.execute(stmt)
        result = stmt.scalars().all()

        if not result:
            return False
        return result
    
    async def delete_chat(self, db: AsyncSession, message_id):
        await db.execute(delete(Chat).where(Chat.id == message_id))
        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True
    
    async def mark_read(self, db: AsyncSession, message_id):
        await db.execute(update(Chat).where(Chat.id == message_id, Chat.read == False).values(read = True))
        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True
    
    async def get_inbox(self, db: AsyncSession, **info):
        