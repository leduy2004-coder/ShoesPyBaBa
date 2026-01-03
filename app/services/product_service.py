from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.schemas.common_schema import PaginationSchema

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def get_products(self, page: int, size: int, filters: dict):
        products, total = self.repo.get_list(page, size, filters)
        
        total_pages = (total + size - 1) // size
        pagination = PaginationSchema(
            page=page, size=size, total=total, total_pages=total_pages
        )
        return products, pagination

    def get_product_detail(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            return None
        return product