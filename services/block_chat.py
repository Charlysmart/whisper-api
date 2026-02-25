from fastapi.background import P
from sqlalchemy import delete, select
from models.block_chat import BlockChat
from sqlalchemy.ext.asyncio import AsyncSession

class BlockChatCRUD:
    def __init__(self):
        pass
      
    async def get_blocked_chat(self, db: AsyncSession, thread: str):
        blocked = await db.execute(select(BlockChat).where(BlockChat.thread == thread))
        result = blocked.scalar_one_or_none()
        if blocked:
            return result
        return False
    
    async def add_block_chat(self, db: AsyncSession, thread: str, user_id: int):
        block_chat = BlockChat(thread = thread, blocked_by = user_id)
        db.add(block_chat)
        try:
            await db.commit()
            await db.refresh(block_chat)
        except:
            await db.rollback()
            return False
        return block_chat
    
    async def delete_block_chat(self, db: AsyncSession, thread: str):
        await db.execute(delete(BlockChat).where(BlockChat.thread == thread))
        try:
            await db.commit()
        except:
            await db.rollback()
            return False
        return True