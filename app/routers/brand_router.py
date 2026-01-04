from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.brand_schema import BrandSchema, CreateBrandSchema, UpdateBrandSchema, BrandPaginationSchema
from app.schemas.base_schema import DataResponse
from app.services.brand_service import BrandService
from app.repositories.brand_repository import BrandRepository
from app.core.security import require_role

router = APIRouter()

def get_brand_service(db: Session = Depends(get_db)) -> BrandService:
    repository = BrandRepository(db)
    return BrandService(repository)

@router.get("/brands", tags=["brands"], description="Get all brands", response_model=DataResponse[BrandPaginationSchema])
async def get_brands(
    limit: int = 10, 
    page: int = 1, 
    keyword: Optional[str] = None,
    service: BrandService = Depends(get_brand_service)
):
    brands = service.get_brands(limit=limit, page=page, keyword=keyword)
    return DataResponse.custom_response(code="200", message="get list brands", data=brands)

@router.post("/brands", tags=["brands"], description="Create a new brand", response_model=DataResponse[BrandSchema])
async def create_brand(data: CreateBrandSchema, service: BrandService = Depends(get_brand_service), current_user: dict = Depends(require_role(["admin"]))):
    brand = service.create_brand(data)
    return DataResponse.custom_response(code="201", message="Create brand successfully", data=brand)

@router.get("/brands/{brand_id}", tags=["brands"], description="Get a brand by id", response_model=DataResponse[BrandSchema])
def get_brand(brand_id: int, service: BrandService = Depends(get_brand_service)):
    brand = service.get_brand(brand_id)
    return DataResponse.custom_response(code="200", message="Get brand by id", data=brand)

@router.delete("/brands/{brand_id}", tags=["brands"], description="Delete a brand by id", response_model=DataResponse[BrandSchema])
def delete_brand(brand_id: int, service: BrandService = Depends(get_brand_service), current_user: dict = Depends(require_role(["admin"]))):
    service.delete_brand(brand_id)
    return DataResponse.custom_response(code="200", message="Delete brand by id", data=None)

@router.put("/brands/{brand_id}", tags=["brands"], description="Update a brand by id", response_model=DataResponse[BrandSchema])
def update_brand(brand_id: int, data: UpdateBrandSchema, service: BrandService = Depends(get_brand_service), current_user: dict = Depends(require_role(["admin"]))):
    brand = service.update_brand(brand_id, data)
    return DataResponse.custom_response(code="200", message="Update brand by id", data=brand)
