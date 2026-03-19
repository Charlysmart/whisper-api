from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from services.image_uploader import CloudinaryService
from utils.oauth import check_user_verified
import shutil, os, uuid

image_router = APIRouter(prefix="/pages", tags=["Pages"])

@image_router.post("/upload_image")
async def upload_image(image: UploadFile = File(...), user: dict = Depends(check_user_verified)):
    result = CloudinaryService.uploadImage(image.file)
    if result:
        return {
            "url" : result["secure_url"],
            "public_id" : result["public_id"]
        }