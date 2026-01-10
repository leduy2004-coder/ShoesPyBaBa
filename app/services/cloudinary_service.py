import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile, HTTPException
from app.core.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name="db8bzpkle",
    api_key="774674856922989",
    api_secret="eBR2PmDP3LQxCcSHMPeKz2QM4uQ"
)

class CloudinaryService:
    @staticmethod
    def upload_file(file: UploadFile) -> dict:
        try:
            # Read file content
            content = file.file.read()
            # Upload the file content to Cloudinary
            result = cloudinary.uploader.upload(content)
            return result
        except Exception as e:
            print(f"DEBUG: Cloudinary Upload Error: {str(e)}")
            import traceback
            traceback.print_exc()
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
