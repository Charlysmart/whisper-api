from fastapi import APIRouter, Depends, HTTPException, status
from database.session import get_db
from services.room import RoomCRUD
from utils.oauth import check_user_verified
from schemas.room import RoomIn, JoinRoomIn
from sqlalchemy.ext.asyncio import AsyncSession
from utils.generate_message_thread import generate_room_thread
from utils.socket import connected_room_users

room_router = APIRouter(prefix="/pages", tags=["Pages"])
roomCrud = RoomCRUD()

@room_router.post("/create_room")
async def create_room(value: RoomIn,  user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    room_thread: str

    while True:
        room_thread = generate_room_thread() 
        thread = await roomCrud.select_room("single", **{"room_thread" : room_thread})
        if not thread:
            break
    try:
        stmt = await roomCrud.create_room(db, **{"room_name" : value.title, "room_thread" : room_thread, "admin" : user["id"], "display_admin" : value.display_admin})
        if stmt:
            join = await roomCrud.join_room(db, **{"room_thread" : room_thread, "user_id" : user["id"]})
            if join:
                return {
                    "thread" : stmt.room_thread,
                    "title" : stmt.room_name
                }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create room! Try again shortly.")
    

@room_router.post("/join_room")
async def join_room(value: JoinRoomIn,  user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    result = await roomCrud.select_room("single", **{"room_thread" : value.thread})

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room does not exist!")
    output = await roomCrud.select_joined_room("single", **{"room_thread" : value.thread, "user_id" : user["id"]})
    
    if output:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already in room!")
    add_user = await roomCrud.join_room(db, **{"room_thread" : value.thread, "user_id" : user["id"]})
    if add_user:
        for uid, sockets in connected_room_users[value.thread].items():
            for ws in sockets:
                await ws.send_json({
                    "type" : "update",
                    "data" : True
                })
        return {
            "message" : f"{result.room_name} joined!"
        }
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to join room! Try again shortly.")


@room_router.get("/joined_rooms")
async def joined_rooms(user: dict = Depends(check_user_verified), db: AsyncSession = Depends(get_db)):
    result = await roomCrud.select_joined_room("all", **{"user_id" : user["id"]})

    if result:
        rooms = []
        for j in result:
            result = await roomCrud.select_room("single", **{"room_thread" : j.room_thread})
            rooms.append({
                "room_name" : result.room_name,
                "room_thread" : j.room_thread
            })
        return {
            "rooms" : rooms
        }  
    return None