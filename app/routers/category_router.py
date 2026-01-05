from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.category_schema import CategorySchema, CreateCategorySchema, UpdateCategorySchema, CategoryPaginationSchema
from app.schemas.base_schema import DataResponse
from app.services.category_service import CategoryService
from app.repositories.category_repository import CategoryRepository
from app.core.security import require_role

router = APIRouter()

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    repository = CategoryRepository(db)
    return CategoryService(repository)

@router.get("/categories", tags=["categories"], description="Get all categories", response_model=DataResponse[CategoryPaginationSchema])
async def get_categories(
    limit: int = 10, 
    page: int = 1, 
    keyword: Optional[str] = None,
    service: CategoryService = Depends(get_category_service)
):
    categories = service.get_categories(limit=limit, page=page, keyword=keyword)
    return DataResponse.custom_response(code="200", message="get list categories", data=categories)

@router.post("/categories", tags=["categories"], description="Create a new category", response_model=DataResponse[CategorySchema])
async def create_category(data: CreateCategorySchema, service: CategoryService = Depends(get_category_service), current_user: dict = Depends(require_role(["admin"]))):
    category = service.create_category(data)
    return DataResponse.custom_response(code="201", message="Create category successfully", data=category)

@router.get("/categories/{category_id}", tags=["categories"], description="Get a category by id", response_model=DataResponse[CategorySchema])
def get_category(category_id: int, service: CategoryService = Depends(get_category_service)):
    category = service.get_category(category_id)
    return DataResponse.custom_response(code="200", message="Get category by id", data=category)

@router.delete("/categories/{category_id}", tags=["categories"], description="Delete a category by id", response_model=DataResponse[CategorySchema])
def delete_category(category_id: int, service: CategoryService = Depends(get_category_service), current_user: dict = Depends(require_role(["admin"]))):
    service.delete_category(category_id)
    return DataResponse.custom_response(code="200", message="Delete category by id", data=None)

@router.put("/categories/{category_id}", tags=["categories"], description="Update a category by id", response_model=DataResponse[CategorySchema])
def update_category(category_id: int, data: UpdateCategorySchema, service: CategoryService = Depends(get_category_service), current_user: dict = Depends(require_role(["admin"]))):
    category = service.update_category(category_id, data)
    return DataResponse.custom_response(code="200", message="Update category by id", data=category)
