from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models.product_model import Product

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_list(self, page: int, size: int, filters: dict):
        query = self.db.query(Product).filter(Product.status == 'active')

        if filters.get("keyword"):
            search = f"%{filters['keyword']}%"
            query = query.filter(Product.name.ilike(search))

        if filters.get("category_id"):
            query = query.filter(Product.category_id == filters["category_id"])

        if filters.get("brand_id"):
            query = query.filter(Product.brand_id == filters["brand_id"])

        if filters.get("min_price"):
            query = query.filter(Product.price >= filters["min_price"])

        if filters.get("max_price"):
            query = query.filter(Product.price <= filters["max_price"])

        sort_by = filters.get("sort_by")
        if sort_by == "price_asc":
            query = query.order_by(asc(Product.price))
        elif sort_by == "price_desc":
            query = query.order_by(desc(Product.price))
        elif sort_by == "newest":
            query = query.order_by(desc(Product.created_at))
        else:
             query = query.order_by(desc(Product.id))

        total = query.count()
        products = query.offset((page - 1) * size).limit(size).all()

        return products, total
    
    def get_by_id(self, product_id: int):
        return self.db.query(Product).filter(Product.id == product_id, Product.status == 'active').first()