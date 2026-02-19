from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from schemas.anonymous import AnonymousIn
from services.anonymous import AnonymousCRUD
from services.notification import NotificationCRUD
from services.users import UserCRUD
from utils import generate_message_thread
from utils.oauth import check_user_verified
from utils.socket import connected_notify_users, connected_anonymous_users


anonymous_router = APIRouter(prefix="/pages", tags=["Pages"])
userCrud = UserCRUD()
anonymousCrud = AnonymousCRUD()
notificationCrud = NotificationCRUD()

# Send anonymous
@anonymous_router.post("/send_anonymous")
async def send_anonymous(content: AnonymousIn, db: AsyncSession = Depends(get_db), sender: dict = Depends(check_user_verified)):
    anonymous_content = content.model_dump()
    receiver = await userCrud.get_user(db, "single", None, {"custom_username" : content.username})
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid User! Kindly check the username correctly.")
    if sender["id"] == receiver.id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Can't send anonymous to self!")
    message_thread:str
    while True:
        message_thread = generate_message_thread()
        result = await anonymousCrud.get_anonymous(db, {"message_thread" : message_thread})
        if not result:
            break
    
    anonymous_content.update({
        "message_thread" : message_thread,
        "sender_id" : sender["id"],
        "receiver_id" : receiver.id
    })
    del anonymous_content["username"]
    insert = await anonymousCrud.post_anonymous(db, anonymous_content)

    if insert:
        notify = await notificationCrud.add_notification(db, {
            "type" : "message", 
            "notify_id" : message_thread, 
            "user_id" : receiver.id
        })

        receiver_notify = connected_notify_users.get(insert.receiver_id)
        if receiver_notify:
            await receiver_notify.send_json({
                "type": "notification",
                "data": {
                    "type" : notify.type,
                    "content" : notify.content,
                    "notify_id" : notify.notify_id,
                    "added" : str(notify.added),
                    "read" : notify.read,
                    "id" : notify.id
                }
            })
        
        receiver_anonymous = connected_anonymous_users.get(insert.receiver_id)
        if receiver_anonymous:
            await receiver_anonymous.send_json({
                "type" : "anonymous",
                "data" : {
                    "content" : insert.content,
                    "message_thread" : insert.message_thread,
                    "sent_at" : str(insert.sent_at),
                    "id" : insert.id,
                    "read" : insert.read,
                    "replied" : insert.replied,
                    "be_replied" : insert.be_replied
                }
            })
        return {
            "message" : "Message Sent!"
        }
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An error occurred while sending message! Kindly try again shortly.")


@anonymous_router.get("/get_anonymous")
async def display_anonymous(filter: str, page: int = 1, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    limit = 10
    skip = (page - 1) * limit
    if filter == "all":
        stmt = await db.execute(select(Anonymous).where(Anonymous.receiver_id == user["id"]).order_by(Anonymous.sent_at.desc()).offset(skip).limit(limit))
    elif filter == "unread": 
        stmt = await db.execute(select(Anonymous).where(Anonymous.receiver_id == user["id"], Anonymous.read == False).order_by(Anonymous.sent_at.desc()).offset(skip).limit(limit))
    elif filter == "replied": 
        stmt = await db.execute(select(Anonymous).where(Anonymous.receiver_id == user["id"], Anonymous.replied == True).order_by(Anonymous.sent_at.desc()).offset(skip).limit(limit))
    else:
        stmt = await db.execute(select(Anonymous).where(Anonymous.receiver_id == user["id"]).order_by(Anonymous.sent_at.desc()).offset(skip).limit(limit))

    result = stmt.scalars().all()

    messages = await db.execute(select(func.count()).select_from(Anonymous).where(Anonymous.receiver_id == user["id"]))
    message_count = messages.scalar_one()
    anonymous = []
    for r in result:
        anonymous.append({
            "content" : r.content,
            "message_thread" : r.message_thread,
            "sent_at" : r.sent_at,
            "id" : r.id,
            "replied" : r.replied,
            "read" : r.read,
            "be_replied" : r.be_replied
        })
    return {
        "anonymous" : anonymous,
        "count" : message_count
    }

@anonymous_router.websocket("/new_anonymous")
async def new_anonymous(websocket: WebSocket):
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
        
    connected_anonymous_users[user["id"]] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_anonymous_users.pop(user["id"], None)
    except Exception as e:
        print("WebSocket anonymous error:", e)


@anonymous_router.patch("/reply_anonymous/{thread}")
async def reply_message(thread: str, db: AsyncSession = Depends(get_db), user: dict = Depends(check_user_verified)):
    stmt = await db.execute(update(Anonymous).where(Anonymous.message_thread == thread, Anonymous.receiver_id == user["id"]).values(replied = True, read = True))
    await db.commit()


    if stmt.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Failed to start a chat!")
    to_transfer = await db.execute(select(Anonymous).where(Anonymous.message_thread == thread))
    transfer = to_transfer.scalar_one_or_none()
    set_chat = Chat(message_thread = transfer.message_thread, sender_id = transfer.sender_id, content = transfer.content, read = True, sent_at = transfer.sent_at, receiver_id = transfer.receiver_id)
    db.add(set_chat)
    try:
        await db.commit()
        await db.refresh(set_chat)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to initialize chat!")
    
@anonymous_router.patch("/markRead/{thread}")
async def mark_read(thread: str, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No thread attached")
    stmt = await db.execute(update(Anonymous).where(Anonymous.message_thread == thread, Anonymous.receiver_id == user["id"]).values(read = True))
    await db.commit()
    if stmt.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to mark as read!")
    return True
    

    