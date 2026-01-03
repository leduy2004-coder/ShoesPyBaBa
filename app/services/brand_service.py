from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.repositories.brand_repository import BrandRepository
from app.schemas.brand_schema import BrandSchema, CreateBrandSchema, UpdateBrandSchema

class BrandService:
    def __init__(self, repository: BrandRepository):
        self.repository = repository

    def get_brands(
        self, 
        limit: int = 10, 
        page: int = 1, 
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        skip = (page - 1) * limit
        items, total = self.repository.get_all(skip=skip, limit=limit, keyword=keyword)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }

    def create_brand(self, brand_data: CreateBrandSchema) -> BrandSchema:
        return self.repository.create(brand_data.model_dump())

    def get_brand(self, brand_id: int) -> BrandSchema:
        brand = self.repository.get_by_id(brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        return brand

    def update_brand(self, brand_id: int, brand_data: UpdateBrandSchema) -> BrandSchema:
        brand = self.repository.get_by_id(brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        update_data = brand_data.model_dump(exclude_unset=True)
        return self.repository.update(brand, update_data)

    def delete_brand(self, brand_id: int) -> None:
        brand = self.repository.get_by_id(brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        self.repository.delete(brand)
