from pydantic import BaseModel

class FileResponse(BaseModel):
    public_id: str
    url: str
    format: str
    resource_type: str
    created_at: str

class FileProductResponse(BaseModel):
    public_id: str
    url: str

