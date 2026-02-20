from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from utils.oauth import check_user_verified
import shutil, os, uuid

image_router = APIRouter(prefix="/pages", tags=["Pages"])

@image_router.post("/upload_image")
async def upload_image(image: UploadFile = File(...), user: dict = Depends(check_user_verified)):
    FILEPATH = "uploads/private"
    os.makedirs(FILEPATH, exist_ok=True)

    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Image type")
    FILENAME = f"{uuid.uuid4()}_{image.filename}"
    with open(f"{FILEPATH}/{FILENAME}", "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return {"image" : FILENAME}


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads", "private")

@image_router.get("/image/{fileName}")
async def get_chat_image(fileName: str, user: dict = Depends(check_user_verified)):
    file_path = os.path.join(UPLOAD_DIR, fileName)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)