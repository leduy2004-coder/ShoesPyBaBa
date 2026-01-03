from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.db.base import get_db
from sqlalchemy.orm import Session
from app.models.product_model import Product
from app.schemas.product_schema import ProductSchema, CreateProductSchema, UpdateProductSchema, ProductResponse, ProductFilter
from app.schemas.base_schema import DataResponse
from app.schemas.common_schema import PaginationSchema, ResponseSchema
from app.services.product_service import ProductService
from app.models.user_model import User
from app.middleware.authenticate import authenticate as get_current_user
from datetime import datetime

router = APIRouter()

@router.get("/products", tags=["products"], description="Get all products", response_model=DataResponse[list[ProductSchema]])
async def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.deleted_at == None).all()
    return DataResponse.custom_response(code="200", message="get list products", data=products)

@router.post("/products", tags=["products"], description="Create a new product", response_model=DataResponse[ProductSchema])
async def create_product(data: CreateProductSchema, db: Session = Depends(get_db)):
    db_product = Product(**data.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return DataResponse.custom_response(code="201", message="Create product page", data=db_product)

@router.get("/products/{product_id}", tags=["products"], description="Get a product by id", response_model=DataResponse[ProductSchema])
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return DataResponse.custom_response(code="404", message="Product not found", data=None)
    return DataResponse.custom_response(code="200", message="Get product by id", data=product)

@router.delete("/products/{product_id}", tags=["products"], description="Delete a product by id", response_model=DataResponse[ProductSchema])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return DataResponse.custom_response(code="404", message="Product not found", data=None)
    
    product.deleted_at = datetime.now()
    db.commit()
    return DataResponse.custom_response(code="200", message="Delete product by id", data=None)

@router.put("/products/{product_id}", tags=["products"], description="Update a product by id", response_model=DataResponse[ProductSchema])
def update_product(product_id: int, data: UpdateProductSchema, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return DataResponse.custom_response(code="404", message="Product not found", data=None)
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return DataResponse.custom_response(code="200", message="Update product by id", data=product)

@router.get("/products", tags=["products"], description="Get products with pagination and filters", response_model=ResponseSchema[list[ProductResponse]])
def search_products(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProductService(db)
    filters = {
        "keyword": keyword, "category_id": category_id,
        "min_price": min_price, "max_price": max_price, "sort_by": sort_by
    }
    
    data, pagination = service.get_products(page, size, filters)
    
    return ResponseSchema(
        data=data,
        message="Lấy danh sách sản phẩm thành công",
        pagination=pagination
    )

@router.get("/products/{product_id}", tags=["products"], description="Get product detail by id", response_model=ResponseSchema[ProductResponse])
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProductService(db)
    product = service.get_product_detail(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
        
    return ResponseSchema(data=product, message="Lấy chi tiết thành công")