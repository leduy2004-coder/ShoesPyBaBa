from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.db.base import get_db
from sqlalchemy.orm import Session
from app.models.product_model import Product
from app.schemas.product_schema import ProductSchema, CreateProductSchema, UpdateProductSchema, ProductResponse, ProductFilter, ProductResponseDetail
from app.schemas.base_schema import DataResponse
from app.schemas.common_schema import PaginationSchema, ResponseSchema
from app.services.product_service import ProductService
from app.models.user_model import User
from app.middleware.authenticate import authenticate as get_current_user
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.product_schema import ProductSchema, CreateProductSchema, UpdateProductSchema, ProductPaginationSchema
from app.schemas.base_schema import DataResponse
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository
from app.core.security import require_role


router = APIRouter()

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    repository = ProductRepository(db)
    return ProductService(repository)

@router.get("/products", tags=["products"], description="Get all products", response_model=DataResponse[ProductPaginationSchema])
async def get_products(
    limit: int = 10, 
    page: int = 1, 
    keyword: Optional[str] = None, 
    search_type: str = "title",
    service: ProductService = Depends(get_product_service)
):
    products = service.get_products(limit=limit, page=page, keyword=keyword, search_type=search_type)
    return DataResponse.custom_response(code="200", message="get list products", data=products)

@router.post("/products", tags=["products"], description="Create a new product", response_model=DataResponse[ProductSchema])
async def create_product(data: CreateProductSchema, service: ProductService = Depends(get_product_service), current_user: dict = Depends(require_role(["admin"]))):
    product = service.create_product(data)
    return DataResponse.custom_response(code="201", message="Create product page", data=product)

@router.get("/products/{product_id}", tags=["products"], description="Get a product by id", response_model=DataResponse[ProductSchema])
def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    product = service.get_product(product_id)
    return DataResponse.custom_response(code="200", message="Get product by id", data=product)

@router.delete("/products/{product_id}", tags=["products"], description="Delete a product by id", response_model=DataResponse[ProductSchema])
def delete_product(product_id: int, service: ProductService = Depends(get_product_service), current_user: dict = Depends(require_role(["admin"]))):
    service.delete_product(product_id)
    return DataResponse.custom_response(code="200", message="Delete product by id", data=None)

@router.put("/products/{product_id}", tags=["products"], description="Update a product by id", response_model=DataResponse[ProductSchema])
def update_product(product_id: int, data: UpdateProductSchema, service: ProductService = Depends(get_product_service), current_user: dict = Depends(require_role(["admin"]))):
    product = service.update_product(product_id, data)
    return DataResponse.custom_response(code="200", message="Update product by id", data=product)

@router.get("/products", tags=["products"], description="Get products with pagination and filters", response_model=ResponseSchema[list[ProductResponse]])
def search_products(
    filter_params: ProductFilter = Depends(),

    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    service = ProductService(db)
    data, pagination = service.get_products(page, size, filter_params)
    
    return ResponseSchema(
        code=200,
        message="Get products success",
        data=data,
        pagination=pagination
    )

@router.get("/products/{product_id}", tags=["products"], description="Get product detail by id", response_model=DataResponse[ProductResponseDetail])
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    service = ProductService(db)
    product = service.get_product_detail(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
        
    return ResponseSchema(code=200, message="Get detail product success", data=product)