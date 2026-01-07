
from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.schemas.common_schema import PaginationSchema
from app.schemas.product_schema import ProductResponse, ProductSchema, CreateProductSchema, UpdateProductSchema, ProductFilter
from app.models.category_model import Category
from app.models.brand_model import Brand
from typing import List, Optional
from fastapi import HTTPException
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import ProductSchema, CreateProductSchema, UpdateProductSchema

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def get_products(self, page: int, size: int, filters: ProductFilter):

        # Validate category
        if filters.category_id is not None:
            exists = (
                self.db.query(Category.id)
                .filter(Category.id == filters.category_id)
                .first()
            )
            if not exists:
                return [], self._empty_pagination(page, size)

        # Validate brand
        if filters.brand_id is not None:
            exists = (
                self.db.query(Brand.id)
                .filter(Brand.id == filters.brand_id)
                .first()
            )
            if not exists:
                return [], self._empty_pagination(page, size)

        products, total = self.repo.get_list(page, size, filters)

        return products, {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": (total + size - 1) // size
        }

    def _empty_pagination(self, page, size):
        return {
            "page": page,
            "size": size,
            "total": 0,
            "total_pages": 0
        }

    def get_product_detail(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            return None
        return product

class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def get_products(
        self, 
        limit: int = 10, 
        page: int = 1, 
        keyword: Optional[str] = None, 
        search_type: str = "title"
    ) -> dict:
        skip = (page - 1) * limit
        items, total = self.repository.get_all(skip=skip, limit=limit, keyword=keyword, search_type=search_type)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }

    def create_product(self, product_data: CreateProductSchema) -> ProductSchema:
        return self.repository.create(product_data.model_dump())

    def get_product(self, product_id: int) -> ProductSchema:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
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

