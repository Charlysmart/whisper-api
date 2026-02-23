from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.connect import SessionLocal
from models.chat import Chat
from schemas.inbox import FetchIn, Filter

class InboxCRUD:
    def __init__(self):
        pass

    async def send_chat(self, **info):
        async with SessionLocal() as db:
            chat = Chat(**info)
            db.add(chat)

            try:
                await db.commit()
                await db.refresh(chat)
            except:
                await db.rollback()
                return False
            return chat
    
    async def get_chat(self, fetch: FetchIn, **info):
        async with SessionLocal() as db:
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
                return None
            print("result: ", result)
            return result
    
    async def delete_chat(self, message_id, user_id):
        async with SessionLocal() as db:
            await db.execute(delete(Chat).where(Chat.id == message_id, Chat.sender_id == user_id))
            try:
                await db.commit()
            except:
                await db.rollback()
                return False
            return True
    
    async def mark_chat_read(self, message_id, user_id):
        async with SessionLocal() as db:
            await db.execute(update(Chat).where(Chat.id == message_id, Chat.receiver_id == user_id, Chat.read == False).values(read = True))
            try:
                await db.commit()
            except:
                await db.rollback()
                return False
            return True
    
    async def mark_inbox_read(self, db: AsyncSession, message_thread, user_id):
        await db.execute(update(Chat).where(Chat.message_thread == message_thread, Chat.receiver_id == user_id, Chat.read == False).values(read = True))
        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True
    
    async def get_inbox(self, db: AsyncSession, id: int, page: int, filter: Filter = "all"):
        LIMIT = 10
        OFFSET = (page - 1) * 10
        subq = select(Chat.message_thread, func.max(Chat.sent_at).label("time_sent"), func.max(Chat.id).label("id")).where(or_(Chat.receiver_id == id, Chat.sender_id == id))
        if filter == "unread":
            subq = subq.where(Chat.read == False)
        subq = subq.group_by(Chat.message_thread).subquery()

        stmt = await db.execute(select(Chat).join(subq, (Chat.message_thread == subq.c.message_thread) & (Chat.sent_at == subq.c.time_sent) & (Chat.id == subq.c.id)).order_by(Chat.sent_at.desc()).offset(OFFSET).limit(LIMIT))
        count = await db.execute(select(func.count(func.distinct(Chat.message_thread))).select_from(Chat).where(or_(Chat.receiver_id == id, Chat.sender_id == id)))
        inbox = stmt.scalars().all()
        inbox_count = count.scalar_one_or_none()

        if inbox:
            return {
                "count" : inbox_count if inbox_count else 0,
                "inbox" : inbox
            }
        
        else:
            return None