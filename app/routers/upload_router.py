from fastapi import APIRouter, UploadFile, File, status
from app.services.cloudinary_service import CloudinaryService
from app.schemas.file_schema import FileResponse

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=list[FileResponse], status_code=status.HTTP_201_CREATED)
async def upload_files(
    file: UploadFile = File(None),
    files: list[UploadFile] = File(None)
):
    """
    Upload one or multiple files to Cloudinary.
    Supports both 'file' and 'files' field names.
    """
    all_files = []
    if file:
        all_files.append(file)
    if files:
        all_files.extend(files)

    if not all_files:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No file or files provided")

    uploaded_results = []
    for f in all_files:
        result = CloudinaryService.upload_file(f)
        uploaded_results.append(FileResponse(
            public_id=result.get("public_id"),
            url=result.get("secure_url"),
            format=result.get("format"),
            resource_type=result.get("resource_type"),
            created_at=str(result.get("created_at"))
        ))
    return uploaded_results

@router.delete("/{public_id}")
async def delete_file(public_id: str):
    """
    Delete a file from Cloudinary using its public_id.
    """
    result = CloudinaryService.delete_file(public_id)
    return {"message": "File deleted successfully", "result": result}

@router.get("/{public_id}")
async def get_file(public_id: str):
    """
    Get file details from Cloudinary.
    """
    result = CloudinaryService.get_file(public_id)
    return result
