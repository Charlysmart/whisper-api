from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from database.connect import SessionLocal
from database.session import get_db
from models.whisperroom import Whisperroom
from services.room import RoomCRUD
from services.whisperroom import WhisperroomCRUD
from utils.oauth import check_user_verified, check_token
from utils.time_extract import extract_time
from utils.socket import connected_room_users

whisperroom_router = APIRouter(prefix="/pages", tags=["Pages"])
whisperroomCrud = WhisperroomCRUD()
roomCrud = RoomCRUD()

@whisperroom_router.websocket("/send_whisperroom/{room_thread}")
async def post_whisperroom(room_thread: str, websocket: WebSocket):
    await websocket.accept()

    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=1008)
        return

    async with SessionLocal() as db:
        try:
            user = await check_token(token, db)
        except:
            await websocket.close(1008)
            return

    if room_thread not in connected_room_users:
        connected_room_users[room_thread] = {} 

    if user["id"] not in connected_room_users[room_thread]:
        connected_room_users[room_thread][user["id"]] = set()

    connected_room_users[room_thread][user["id"]].add(websocket)

    try:
        while True:
            user_id = user["id"]
            data = await websocket.receive_json()
            msg_type = data.get("type")
            msg_data = data.get("data")
            if msg_type == "message":

                if not msg_data.get("image") and not msg_data.get("content", "").strip():
                    await websocket.send_json({
                        "type": "error",
                        "data": "Can't send empty field!"
                    })
                    continue

                room_exists = await roomCrud.select_room("single", room_thread=room_thread)
                if not room_exists:
                    await websocket.send_json({
                        "type": "error",
                        "data": "Room does not exist!"
                    })
                    continue

                user_in_room = await roomCrud.select_joined_room(
                    "single",
                    room_thread=room_thread,
                    user_id=user_id
                )

                if not user_in_room:
                    await websocket.send_json({
                        "type": "error",
                        "data": "You're not a part of this conversation!"
                    })
                    continue

                reply_parent = None
                if msg_data.get("reply_to") is not None:
                    reply_parent = await whisperroomCrud.get_chat(
                        "single",
                        id=msg_data.get("reply_to"),
                        room_thread=room_thread
                    )

                    if not reply_parent:
                        await websocket.send_json({
                            "type": "error",
                            "data": "Invalid reply message"
                        })
                        continue

                chat = await whisperroomCrud.post_chat(
                    sender_id=user_id,
                    content=msg_data.get("content"),
                    room_thread=room_thread,
                    image=msg_data.get("image"),
                    reply_to=msg_data.get("reply_to")
                )

                print("Chat: ", chat)
                if not chat:
                    await websocket.send_json({
                        "type": "error",
                        "data": "Failed to send message"
                    })
                    continue

                reply = reply_parent.content if reply_parent else None
                admin = room_exists.admin == user_id and room_exists.display_admin

                message_payload = {
                    "sender": chat.sender_id == user_id,
                    "message_thread": chat.room_thread,
                    "image": chat.image,
                    "content": chat.content,
                    "reply_to": reply,
                    "time": str(chat.sent_at),
                    "id": chat.id,
                    "admin": admin
                }

                await websocket.send_json({
                    "type": "message",
                    "data": message_payload
                })

                for uid, sockets in connected_room_users[room_thread].items():
                    for ws in sockets:
                        if ws != websocket:
                            await ws.send_json({
                                "type": "message",
                                "data": {
                                    **message_payload,
                                    "sender": chat.sender_id != user_id
                                }
                            })
                
            elif msg_type == "delete":
                deleted = await whisperroomCrud.delete_chat(msg_data, user_id)
                if deleted:
                    await websocket.send_json({
                        "type": "delete",
                        "data": msg_data
                    })
                    for uid, sockets in connected_room_users[room_thread].items():
                        for ws in sockets:
                            if ws != websocket:
                                await ws.send_json({
                                    "type": "delete",
                                    "data": msg_data
                                })

    except WebSocketDisconnect:
        connected_room_users[room_thread][user_id].discard(websocket)

        if not connected_room_users[room_thread][user_id]:
            del connected_room_users[room_thread][user_id]

        if not connected_room_users[room_thread]:
            del connected_room_users[room_thread]


@whisperroom_router.get("/whisperroom/{room_thread}")
async def get_whisperroom(room_thread: str, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    result = await roomCrud.select_room("single", **{"room_thread" : room_thread})
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room does not exist!")
    
    check_user = await roomCrud.select_joined_room("single", **{"room_thread" : room_thread, "user_id" : user["id"]})

    if not check_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You're not a part of this conversation!")
    
    chat = await whisperroomCrud.get_chat("all", **{"room_thread" : room_thread})
    get_count = await roomCrud.get_room_count(**{"room_thread" : room_thread})

    messages = []
    for c in chat:
        parent_msg = await db.get(Whisperroom, c.reply_to)  # fetch message by id
        parent_content = parent_msg.content if parent_msg else None
        messages.append({
            "id" : c.id,
            "content" : c.content,
            "image" : c.image,
            "time" : c.sent_at,
            "reply_to" : parent_content,
            "sender" : c.sender_id == user["id"],
            "admin" : result.admin == c.sender_id and result.display_admin == True
        })
    return {
        "room_name": result.room_name,
        "messages": messages,
        "count" : get_count,
        "is_admin" : result.admin == user["id"]
    }


@whisperroom_router.get("/reply_whisperroom")
async def get_whisperroom(id: int, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    result = await whisperroomCrud.get_chat("single", **{"id" : id})

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot reply to this message!")
    return result.content


@whisperroom_router.delete("/leave_room/{thread}")
async def leave_room(thread, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    if thread:
        stmt = await roomCrud.leave_room(thread, user["id"], db)
        if stmt:
            for uid, sockets in connected_room_users[thread].items():
                for ws in sockets:
                    await ws.send_json({
                        "type" : "update",
                        "data" : False
                    })
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to leave room!")

@whisperroom_router.delete("/dissolve_room/{thread}")
async def dissolve_room(thread, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    if thread:
        status_check = await roomCrud.select_room("single", **{"room_thread" : thread})
        
        if status_check.admin != user["id"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have right to dissolve this room")
        stmt = await roomCrud.delete_room(db, thread, user["id"])
        if stmt:
            for uid, sockets in connected_room_users[thread].items():
                for ws in sockets:
                    await ws.send_json({
                        "type" : "dissolve",
                        "data" : True
                    })
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to dissolve room!")
        