from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from database.connect import SessionLocal
from database.session import get_db
from models.chat import Chat
from services.anonymous import AnonymousCRUD
from services.inbox import InboxCRUD
from services.notification import NotificationCRUD
from utils.time_extract import extract_time
from utils.oauth import check_user_verified, check_token
from utils.socket import connected_chat_users, connected_inbox_users, connected_notify_users

chat_router = APIRouter(prefix="/pages", tags=["Pages"])
anonymousCrud = AnonymousCRUD()
chatCrud = InboxCRUD()
notificationCrud = NotificationCRUD()

@chat_router.websocket("/send_chat")
async def reply_chat(websocket: WebSocket):
    await websocket.accept()

    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=1008)
        return
    
    async with SessionLocal() as db:
        try:
            user = await check_token(token, db)
        except Exception:
            await websocket.close(code=1008)
            return
    
    connected_chat_users[user["id"]] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            id:int = user["id"]

            msg_type = data.get("type")
            msg_data = data.get("data")

            if msg_type == "message":
                thread_exist = await anonymousCrud.get_single_anonymous(**{"message_thread" : msg_data["message_thread"]})

                if not thread_exist:
                    await websocket.send_json({
                        "type": "error",
                        "data": "Conversation not found"
                    })
                
                if thread_exist.sender_id == id:
                    receiver = thread_exist.receiver_id
                elif thread_exist.receiver_id == id:
                    receiver = thread_exist.sender_id
                else:
                    await websocket.send_json({
                        "type": "error",
                        "data": "You are not part of this conversation"
                    })
                
                if not msg_data.get("message", "").strip() and not msg_data.get("image"):
                    await websocket.send_json({
                        "type": "error",
                        "data": "Can't send empty message!"
                    })
                
                if msg_data.get("reply_to") is not None:
                    check_reply = await chatCrud.get_chat("single", **{
                        "id" : msg_data.get("reply_to"),
                        "message_thread" : msg_data["message_thread"]}
                    )

                    if not check_reply:
                        await websocket.send_json({
                            "type": "error",
                            "data": "Invalid reply message"
                        })
                    
                message_handler = await chatCrud.send_chat(
                    content = msg_data.get("message", ""),
                message_thread = msg_data["message_thread"], 
                    sender_id = user["id"], 
                    image = msg_data.get("image"),
                    receiver_id = receiver, 
                    reply_to = msg_data.get("reply_to")
                )

                if not message_handler:
                    await websocket.send_json({
                        "type": "error",
                        "data": "Can't send message"
                    })

                if message_handler:
                    send_message = message_handler
                    reply = check_reply.content if msg_data.get("reply_to") else None
                    
                    await websocket.send_json({
                        "type": "message",
                        "data": {
                            "sender" : send_message.sender_id == id,
                            "message_thread" : send_message.message_thread,
                            "image" : send_message.image,
                            "content" : send_message.content,
                            "sent_at" : extract_time(send_message.sent_at),
                            "id" : send_message.id,
                            "read" : send_message.read,
                            "reply_to" : reply
                        }
                    })
                
                    receiver_ws = connected_chat_users.get(receiver)
                    if receiver_ws:
                        await receiver_ws.send_json({
                        "type": "message",
                        "data": {
                            "sender" : send_message.sender_id != id,
                            "message_thread" : send_message.message_thread,
                            "image" : send_message.image,
                            "content" : send_message.content,
                            "sent_at" : extract_time(send_message.sent_at),
                            "id" : send_message.id,
                            "read" : send_message.read,
                            "reply_to" : reply
                        }
                    })
                        
                    receiver_inbox_ws = connected_inbox_users.get(receiver)
                    if receiver_inbox_ws:
                        await receiver_inbox_ws.send_json({
                            "type": "inbox_message",
                            "data": {
                                "content" : send_message.content,
                                "message_thread" : send_message.message_thread,
                                "image" : (not send_message.image),
                                "read" : send_message.read is False and send_message.receiver_id == id,
                                "sent_at" : str(send_message.sent_at)
                            }
                        })
            elif msg_type == "read_receipt":
                message_id = msg_data.get("message_id")
                if not message_id:
                    continue
                await chatCrud.mark_chat_read(message_id, id)
            elif msg_type == "delete":
                message_id = msg_data
                if not message_id:
                    continue
                await chatCrud.delete_chat(message_id, id)
                await websocket.send_json({
                    "type": "delete",
                    "data": message_id
                })

                receiver_chat_ws = connected_chat_users.get(receiver)
                if receiver_chat_ws:
                    await receiver_chat_ws.send_json({
                        "type": "delete",
                        "data": message_id
                    })
            
    except Exception as e:
        print("WebSocket error:", e)
        connected_chat_users.pop(user["id"], None)

@chat_router.get("/reply_chat")
async def get_reply_content(id: int, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    result = await chatCrud.get_chat("single", **{"id" : id})

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cannot reply to this message!")
    return result.content

@chat_router.get("/chat/{thread}")
async def get_chat(thread: str, user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No thread attached")
    result = await chatCrud.get_chat("all", **{"message_thread" : thread})

    if result:     
        if all(
            chat.sender_id != user["id"] and chat.receiver_id != user["id"]
            for chat in result
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this conversation"
            )
        chat = []
        for c in result:
            parent_msg = await db.get(Chat, c.reply_to)  # fetch message by id
            parent_content = parent_msg.content if parent_msg else None
            chat.append({
                "sender" : c.sender_id == user["id"],
                "message_thread" : c.message_thread,
                "content" : c.content,
                "image" : c.image,
                "sent_at" : extract_time(c.sent_at),
                "id" : c.id,
                "read" : c.read,
                "reply_to" : parent_content
            })
        return chat
    return {
        "chat": []
    }
