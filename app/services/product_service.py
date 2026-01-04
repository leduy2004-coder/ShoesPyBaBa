from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.schemas.common_schema import PaginationSchema
from app.schemas.product_schema import ProductResponse

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def get_products(self, page: int, size: int, filters: dict):
        result, total = self.repo.get_list(page, size, filters)
        
        data = []
        for prduct_obj, sold_count in result:
            p_data = prduct_obj.__dict__
            p_data['sold_quantity'] = sold_count
            data.append(ProductResponse(**p_data))

        total_pages = (total + size - 1) // size
        pagination = PaginationSchema(
            page=page, size=size, total=total, total_pages=total_pages
        )
        return data, pagination

    def get_product_detail(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            return None
        return product