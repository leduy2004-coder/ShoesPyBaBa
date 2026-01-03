from sqlalchemy.orm import Session
from app.models.brand_model import Brand
from typing import List, Optional, Tuple

class BrandRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        keyword: Optional[str] = None
    ) -> Tuple[List[Brand], int]:
        query = self.db.query(Brand)
        if keyword:
            query = query.filter(Brand.brand_name.ilike(f"%{keyword}%"))
            
        total = query.count()
        brands = query.offset(skip).limit(limit).all()
        return brands, total

    def get_by_id(self, brand_id: int) -> Optional[Brand]:
        return self.db.query(Brand).filter(Brand.id == brand_id).first()

    def create(self, brand_data: dict) -> Brand:
        db_brand = Brand(**brand_data)
        self.db.add(db_brand)
        self.db.commit()
        self.db.refresh(db_brand)
        return db_brand

    def update(self, brand: Brand, update_data: dict) -> Brand:
        for key, value in update_data.items():
            setattr(brand, key, value)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def delete(self, brand: Brand) -> None:
        self.db.delete(brand)
        self.db.commit()
