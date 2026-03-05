from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from services.anonymous import AnonymousCRUD
from services.block_chat import BlockChatCRUD
from utils.oauth import check_user_verified
from utils.socket import connected_chat_users


block_chat_router = APIRouter(prefix="/pages", tags=["Pages"])

blockChatCrud = BlockChatCRUD()
anonymousCrud = AnonymousCRUD()
@block_chat_router.get("/block_chat")
async def block_chat(thread: str, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    check_thread = await anonymousCrud.get_single_anonymous(**{"message_thread" : thread})
    if not check_thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message thread not found")
    receiver_id: int
    if check_thread.receiver_id != user["id"]:
        receiver_id = check_thread.receiver_id
    else:
        receiver_id = check_thread.sender_id

    receiver_ws = connected_chat_users.get(receiver_id)
    check_blocked = await blockChatCrud.get_blocked_chat(db, thread)
    if not check_blocked:
        add_block = await blockChatCrud.add_block_chat(db, thread, user["id"])
        if not add_block:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't block chat currently")
        if receiver_ws:
            await receiver_ws.send_json({
                "type" : "block",
                "payload" : {
                    "blocked" : True,
                    "blocked_by" : add_block.blocked_by == user["id"]
                }
            })
        return {
            "blocked" : True,
            "blocked_by" : add_block.blocked_by == user["id"]
        }
    if check_blocked.blocked_by == user["id"]:
        unblock_chat = await blockChatCrud.delete_block_chat(db, thread)
        if not unblock_chat:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to unblock chat")
        if receiver_ws:
            await receiver_ws.send_json({
                "type" : "block",
                "payload" : {
                    "blocked" : False,
                    "blocked_by" : None
                }
            })
        return {
            "blocked" : False,
            "blocked_by" : None
        }
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Chat already blocked by alternate party")        