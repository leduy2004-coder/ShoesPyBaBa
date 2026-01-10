from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from fastapi import HTTPException
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import ProductSchema, CreateProductSchema, UpdateProductSchema, ProductFilter
from app.models.category_model import Category
from app.models.brand_model import Brand

class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def get_products(
        self, 
        page: int = 1, 
        size: int = 10, 
        filters: Optional[ProductFilter] = None
    ) -> Tuple[List[any], dict]:
        # Validate category
        if filters and filters.category_id is not None:
            category_exists = self.repository.db.query(Category.id).filter(Category.id == filters.category_id).first()
            if not category_exists:
                return [], self._empty_pagination(page, size)

        # Validate brand
        if filters and filters.brand_id is not None:
            brand_exists = self.repository.db.query(Brand.id).filter(Brand.id == filters.brand_id).first()
            if not brand_exists:
                return [], self._empty_pagination(page, size)

        items, total = self.repository.get_list(page, size, filters)
        
        pagination = {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": (total + size - 1) // size if size > 0 else 0
        }
        return items, pagination

    def get_products_v2(
        self, 
        limit: int = 10, 
        page: int = 1, 
        keyword: Optional[str] = None, 
        search_type: str = "title",
        sort_by: Optional[str] = None
    ) -> dict:
        skip = (page - 1) * limit
        items, total = self.repository.get_all(skip=skip, limit=limit, keyword=keyword, search_type=search_type, sort_by=sort_by)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 0
        }

    def _empty_pagination(self, page, size):
        return {
            "page": page,
            "size": size,
            "total": 0,
            "total_pages": 0
        }

    def create_product(self, product_data: CreateProductSchema) -> ProductSchema:
        return self.repository.create(product_data.model_dump())

    def get_product(self, product_id: int) -> ProductSchema:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    def get_product_detail(self, product_id: int):
        product = self.repository.get_by_id(product_id)
        if not product:
            return None
        return product

    def update_product(self, product_id: int, product_data: UpdateProductSchema) -> ProductSchema:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        update_data = product_data.model_dump(exclude_unset=True)
        return self.repository.update(product, update_data)

    def delete_product(self, product_id: int) -> None:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        self.repository.delete(product)
