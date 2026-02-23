from unittest import result
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.connect import SessionLocal
from models.anonymous import Anonymous
from schemas.anonymous import Filter
class AnonymousCRUD:
    def __init__(self):
        pass

    async def post_anonymous(self, db: AsyncSession, **info):
        anony = Anonymous(**info)
        db.add(anony)
        try:
            await db.commit()
            await db.refresh(anony)
        except:
            await db.rollback()
            return False
        return anony
    
    async def get_anonymous(self, db: AsyncSession, filter: Filter, page: int, user_id: int):
        limit = 10
        skip = (page - 1) * limit

        stmt = select(Anonymous).where(Anonymous.receiver_id == user_id)
        if filter == "unread":
            stmt = stmt.where(Anonymous.read == False)
        stmt = await db.execute(stmt.order_by(Anonymous.sent_at.desc()).offset(skip).limit(limit))            
        result = stmt.scalars().all()

        anony = select(func.count()).select_from(Anonymous).where(Anonymous.receiver_id == user_id)
        if filter == "unread":
            anony = anony.where(Anonymous.read == False)
        elif filter == "replied":
            anony = anony.where(Anonymous.replied == True)
        anony = await db.execute(anony)
        anony_count = anony.scalar_one()

        if result and anony_count:
            return {
                "Anonymous" : result,
                "anony_count" : anony_count
            }
        return False
    
    async def get_single_anonymous(self, **info):
        async with SessionLocal() as db:
            stmt = select(Anonymous)

            for field, value in info.items():
                column = getattr(Anonymous, field, None)
                if not column:
                    continue
                stmt = stmt.where(column == value)
            stmt = await db.execute(stmt)
            result = stmt.scalar_one_or_none()

            if result:
                return result
            return False
    
    async def update_anonymous(self, db: AsyncSession, thread, user_id, values: dict):
        await db.execute(update(Anonymous).where(Anonymous.message_thread == thread, Anonymous.receiver_id == user_id).values(values))
        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True