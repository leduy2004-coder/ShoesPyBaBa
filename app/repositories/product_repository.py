from sqlalchemy.orm import Session
from app.models.product_model import Product
from typing import List, Optional, Tuple, Any
from datetime import datetime

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        keyword: Optional[str] = None, 
        search_type: str = "title"
    ) -> Tuple[List[Product], int]:
        query = self.db.query(Product).filter(Product.deleted_at == None)
        
        if keyword:
            if search_type == "title":
                query = query.filter(Product.name.ilike(f"%{keyword}%"))
            elif search_type == "category":
                query = query.filter(Product.category_id == keyword)
            elif search_type == "brand":
                query = query.filter(Product.brand_id == keyword)
        
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        return products, total

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id, Product.deleted_at == None).first()

    def create(self, product_data: dict) -> Product:
        db_product = Product(**product_data)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update(self, product: Product, update_data: dict) -> Product:
        for key, value in update_data.items():
            setattr(product, key, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        product.deleted_at = datetime.now()
        self.db.commit()
