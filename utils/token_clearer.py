import asyncio
from datetime import datetime, timezone
from sqlalchemy import delete
from database.connect import SessionLocal
from models.tokens import Tokens
from services.store_token import TokenCRUD

# --- Function to clear expired tokens ---
async def clear_expired_tokens():
    async with SessionLocal() as session:
        async with session.begin():
            stmt = delete(Tokens).where((Tokens.expiry <= datetime.now(timezone.utc)) | (Tokens.revoked == True))
            await session.execute(stmt)
        await session.commit()


# --- Background task for periodic cleanup ---
async def periodic_token_cleanup(interval_seconds: int = 3600):
    while True:
        try:
            await clear_expired_tokens()
        except Exception as e:
            print(f"Error clearing tokens: {e}")
        await asyncio.sleep(interval_seconds)