from fastapi import HTTPException, status
from sqlalchemy import select, update
from models.tokens import Tokens
from sqlalchemy.ext.asyncio import AsyncSession

class TokenCRUD:
    def __init__(self):
          pass

    async def store_tokens(self, token:str, reason: str, expiry, id: int, db: AsyncSession):
        stmt = Tokens(token = token, reason = reason, expiry = expiry, user_id = id)
        db.add(stmt)
        try:
            await db.commit()
            await db.refresh(stmt)
        except Exception as e:
            await db.rollback()
            return False
        return True

    async def get_tokens(self, db: AsyncSession, token):
        stmt = await db.execute(select(Tokens).where(Tokens.token == token))
        result = stmt.scalar_one_or_none()
        if result:
            return result
        return False

    async def update_tokens(self, db: AsyncSession, **info):
        stmt = update(Tokens)

        for field, value in info.items():
                column = getattr(Tokens, field, None)
                if not column:
                    continue
                stmt = stmt.where(column == value)
                
        stmt = await db.execute(stmt.values(revoked = True))
        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True