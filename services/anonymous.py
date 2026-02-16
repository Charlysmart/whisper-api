from unittest import result
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.anonymous import Anonymous
class AnonymousCRUD:
    def __init__(self):
        pass

    async def post_anonymous(self, db: AsyncSession, **info):
        anony = Anonymous(**info)
        db.add(anony)
        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True
    
    async def get_anonymous(self, db: AsyncSession, **info):
        stmt = select(Anonymous)
        
        for field, value in info.items():
            column = getattr(Anonymous, field, None)

            if not column:
                continue
            stmt = stmt.where(column == value)
        stmt = await db.execute(stmt)
        result = stmt.scalars().all()

        if not result:
            return False
        return result