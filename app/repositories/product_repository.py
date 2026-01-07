from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, or_
from app.models.product_model import Product
from app.models.order_model import OrderItem, Order
from app.models.product_model import Product
from app.schemas.product_schema import ProductFilter
from typing import List, Optional, Tuple, Any
from datetime import datetime

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_list(self, page: int, size: int, filters: ProductFilter):
        query = (
            self.db.query(
                Product,
                func.coalesce(func.sum(OrderItem.quantity), 0).label("sold_quantity")
            )
            .outerjoin(
                OrderItem, Product.id == OrderItem.product_id
            )
            .outerjoin(
                Order,
                (OrderItem.order_id == Order.id) &
                (Order.status == "delivered")
            )
            .filter(Product.status == "active")
            .group_by(Product.id)
        )

        if filters.keyword is not None:
            query = query.filter(Product.name.ilike(f"%{filters.keyword}%"))

        if filters.category_id is not None:
            query = query.filter(Product.category_id == filters.category_id)

        if filters.brand_id is not None:
            query = query.filter(Product.brand_id == filters.brand_id)

        if filters.min_price is not None:
            query = query.filter(Product.price >= filters.min_price)

        if filters.max_price is not None:
            query = query.filter(Product.price <= filters.max_price)

        if filters.sort_by == "price_asc":
            query = query.order_by(asc(Product.price))
        elif filters.sort_by == "price_desc":
            query = query.order_by(desc(Product.price))
        else:
            query = query.order_by(desc(Product.id))

        total = query.count()
        products = (
            query
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        return products, total
    
    # def get_list(self, page: int, size: int, filters: dict):
    #     query = self.build_query(filters)

    #     total = query.with_entities(Product.id).distinct().count()

    #     items = (
    #         query
    #         .offset((page - 1) * size)
    #         .limit(size)
    #         .all()
    #     )

    #     return items, total
    
    def get_by_id(self, product_id: int):
        return self.db.query(Product).filter(Product.id == product_id, Product.status.in_(['active', 'out_of_stock'])).first()
    
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

    @staticmethod
    def decrement_stock(db: Session, product_id: int, quantity: int, size: Optional[int] = None, color: Optional[str] = None):
        """Decrement stock quantity for a product variant"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
            
        if product.variants:
            # Update variant stock
            updated_variants = []
            variant_found = False
            for v in product.variants:
                if (size is None or v.get('size') == size) and (color is None or v.get('color') == color):
                    current_stock = v.get('stock_quantity', 0)
                    v['stock_quantity'] = max(0, current_stock - quantity)
                    variant_found = True
                updated_variants.append(v)
            
            if variant_found:
                # Use flag_modified or just re-assign to trigger SQLAlchemy update for JSON
                from sqlalchemy.orm.attributes import flag_modified
                product.variants = updated_variants
                flag_modified(product, "variants")
                
                # Check if total stock is 0 to update status
                total_stock = sum(v.get('stock_quantity', 0) for v in product.variants)
                if total_stock <= 0:
                    product.status = "out_of_stock"
                
                db.commit()
                return True
        return False
