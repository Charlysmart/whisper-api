from fastapi import FastAPI
from config.setting import Setting
from database.connect import Base, engine
from contextlib import asynccontextmanager
from routers.auth import auth_router
from routers.users.verification import  verify_router
from routers.users.anonymous  import anonymous_router
from routers.users.chat import chat_router
from routers.users.user_setting import setting_router
from routers.general import general_router
from routers.users.inbox import inbox_router
from routers.users.notification import notification_router
from routers.users.room import room_router
from routers.users.whisperroom import whisperroom_router
from routers.image import image_router
from routers.users.block_chat import block_chat_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

setting = Setting()

app.add_middleware(
    CORSMiddleware,
    allow_origins = setting.origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/")
def home():
    return {"message" : "Hello Render"}

app.include_router(auth_router)
app.include_router(verify_router)
app.include_router(anonymous_router)
app.include_router(chat_router)
app.include_router(setting_router)
app.include_router(general_router)
app.include_router(inbox_router)
app.include_router(notification_router)
app.include_router(room_router)
app.include_router(whisperroom_router)
app.include_router(image_router)
app.include_router(block_chat_router)