# main.py
import os
import asyncio
from fastapi import FastAPI
from config.setting import Setting
from database.connect import Base, engine
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Routers
from routers.auth import auth_router
from routers.verification import verify_router
from routers.users.anonymous import anonymous_router
from routers.users.chat import chat_router
from routers.users.user_setting import setting_router
from routers.general import general_router
from routers.users.inbox import inbox_router
from routers.users.notification import notification_router
from routers.users.room import room_router
from routers.users.whisperroom import whisperroom_router
from routers.image import image_router
from routers.users.block_chat import block_chat_router
from routers.admin.user_management import user_management_router
from routers.admin.dashboard import dashboard_router

# Lifespan with safe DB connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Attempt to connect to DB with timeout
        await asyncio.wait_for(engine.begin().__aenter__(), timeout=5)
        # Optional: create tables if not in production
        if os.getenv("ENV") != "production":
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        print("Database connected successfully")
    except Exception as e:
        print("Database connection failed on startup:", e)
    yield
    try:
        await engine.dispose()
    except:
        pass

# FastAPI app
app = FastAPI(lifespan=lifespan)
setting = Setting()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
@app.get("/")
def root():
    return {"message": "API is running", "PORT": os.getenv("PORT")}

# Include all routers
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
app.include_router(dashboard_router)
app.include_router(user_management_router)

# Uvicorn entry point
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))  # Use platform-assigned port if available
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")