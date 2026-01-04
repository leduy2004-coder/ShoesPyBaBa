from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.repositories.category_repository import CategoryRepository
from app.schemas.category_schema import CategorySchema, CreateCategorySchema, UpdateCategorySchema

class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def get_categories(
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

    def create_category(self, category_data: CreateCategorySchema) -> CategorySchema:
        return self.repository.create(category_data.model_dump())

    def get_category(self, category_id: int) -> CategorySchema:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    def update_category(self, category_id: int, category_data: UpdateCategorySchema) -> CategorySchema:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        update_data = category_data.model_dump(exclude_unset=True)
        return self.repository.update(category, update_data)

    def delete_category(self, category_id: int) -> None:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        self.repository.delete(category)
