from fastapi import HTTPException, status
import cloudinary.uploader

class CloudinaryService:
    @staticmethod
    def uploadImage(file):
        try:
            result = cloudinary.uploader.upload(file)
            return result
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
    def deleteImage(public_id):
        try:
            return cloudinary.uploader.destroy(public_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))