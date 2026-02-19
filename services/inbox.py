from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.chat import Chat
from schemas.inbox import FetchIn, Filter

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
    
    async def get_chat(self, db: AsyncSession, fetch: FetchIn, **info):
        stmt = select(Chat)
        
        for field, value in info.items():
            column = getattr(Chat, field, None)

            if not column:
                continue
            stmt = stmt.where(column == value)
        stmt = await db.execute(stmt)
        if fetch == "all":
            result = stmt.scalars().all()
        elif fetch == "single":
            result = stmt.scalar_one_or_none()

        if not result:
            return False
        return result
    
    async def delete_chat(self, db: AsyncSession, message_id, user_id):
        await db.execute(delete(Chat).where(Chat.id == message_id, Chat.sender_id == user_id))
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
    
    async def get_inbox(self, db: AsyncSession, id: int, page: int, filter: Filter = "all"):
        LIMIT = 10
        OFFSET = (page - 1) * 10
        subq = select(Chat.message_thread, func.max(Chat.sent_at).label("time_sent")).where(or_(Chat.receiver_id == id, Chat.sender_id == id))
        if filter == "unread":
            subq = subq.where(Chat.read == False)
        subq = subq.group_by(Chat.message_thread).subquery()

        stmt = await db.execute(select(Chat).join(subq, (Chat.message_thread == subq.c.message_thread) & (Chat.sent_at == subq.c.time_sent)).distinct(Chat.message_thread).order_by(Chat.message_thread, Chat.sent_at.desc()).offset(OFFSET).limit(LIMIT))
        count = select(func.count(func.distinct(Chat.message_thread))).select_from(Chat).where(or_(Chat.receiver_id == id, Chat.sender_id == id))
        inbox = stmt.scalars().all()
        inbox_count = stmt.scalar_one()

        if inbox:
            return {
                "count" : inbox_count,
                "inbox" : inbox
            }
        
        else:
            return False