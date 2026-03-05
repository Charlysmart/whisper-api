from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from database.connect import SessionLocal
from database.session import get_db
from schemas.notification import Filter
from services.notification import NotificationCRUD
from utils.oauth import check_user_verified, check_token
from utils.socket import connected_notify_users

notification_router = APIRouter(prefix="/pages", tags=["Pages"])
notificationCrud = NotificationCRUD()

@notification_router.get("/get_notification")
async def notification(filter: Filter, page: int = 1, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    result = await notificationCrud.get_notification(db, filter, page, user["id"])

    if result:
        notification = []
        for r in result["notification"]:
            notification.append({
                "type" : r.type,
                "content" : r.content,
                "notify_id" : r.notify_id,
                "added" : r.added,
                "read" : r.read,
                "id" : r.id
            })
        return {
            "notification" : notification,
            "count" : result["notify_count"]
        }
    return {
        "notification" : [],
        "count" : 0
    }


@notification_router.websocket("/new_notification")
async def new_notification(websocket: WebSocket):
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
    connected_notify_users[user["id"]] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_notify_users.pop(user["id"], None)
    except Exception as e:
        print("WebSocket notification error:", e)

@notification_router.patch("/markRead")
async def mark_read(id: int, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    if not id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Id attached")
    read = await notificationCrud.mark_read(id, db)
    if not read:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to mark as read!")
    return False