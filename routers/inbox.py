from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from database.connect import SessionLocal
from database.session import get_db
from schemas.inbox import Filter
from services.inbox import InboxCRUD
from utils.oauth import check_user_verified, check_token
from utils.socket import connected_inbox_users

inbox_router = APIRouter(prefix="/pages", tags=["Pages"])
inboxCrud = InboxCRUD()

@inbox_router.get("/inbox")
async def inbox(page: int, filter: Filter, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    result = await inboxCrud.get_inbox(db, user, page, filter)
    inboxes = result.inbox
    inbox_count = result.inbox_count

    inbox = []
    if not result:
        return None
    for r in inboxes:
        inbox.append({
            "content" : r.content,
            "message_thread" : r.message_thread,
            "image" : (not r.image),
            "read" : not (r.read is False and r.receiver_id == user["id"]),
            "sent_at" : r.sent_at
        })
    return {
        "data" : inbox,
        "count" : inbox_count
    }

@inbox_router.websocket("/get_new_message")
async def getNewMessage(websocket: WebSocket):
    await websocket.accept()
    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(1008)
        return
    async with SessionLocal() as db:
        try:
            user = await check_token(token, db)
        except:
            await websocket.close(1008)
            return
        
    connected_inbox_users[user["id"]] = websocket
    print("🟢 Inbox connected:", user["id"])
        
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
            connected_inbox_users.pop(user["id"], None)
            print("🔴 Inbox disconnected:", user["id"])
    except Exception as e:
        print("WebSocket inbox error:", e)

@inbox_router.patch("/mark_inbox_read")
async def markInboxRead(thread : str, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    stmt = await inboxCrud.mark_inbox_read(db, thread, user)
    if not stmt:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Try again!")