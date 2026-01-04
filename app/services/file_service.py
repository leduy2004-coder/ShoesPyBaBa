import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile, HTTPException
from app.core.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

class FileService:
    @staticmethod
    def upload_file(file: UploadFile) -> dict:
        try:
            # Upload the file to Cloudinary
            result = cloudinary.uploader.upload(file.file)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    @staticmethod
    def delete_file(public_id: str) -> dict:
        try:
            result = cloudinary.uploader.destroy(public_id)
            if result.get("result") != "ok":
                 raise HTTPException(status_code=400, detail="Failed to delete file")
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

    @staticmethod
    def get_file(public_id: str) -> dict:
        try:
            # Get resource details
            result = cloudinary.api.resource(public_id)
            return result
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
