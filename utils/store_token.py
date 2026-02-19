from database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from model.tokens import Tokens
from fastapi import HTTPException, status

async def store_tokens(token:str, reason: str, expiry, id: int, db: AsyncSession):
    stmt = Tokens(token = token, reason = reason, expiry = expiry, user_id = id)
    db.add(stmt)
    try:
        await db.commit()
        await db.refresh(stmt)
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error logging in!!")