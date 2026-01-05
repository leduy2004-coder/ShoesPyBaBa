from sqlalchemy.orm import Session
from app.models.category_model import Category
from typing import List, Optional, Tuple

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        keyword: Optional[str] = None
    ) -> Tuple[List[Category], int]:
        query = self.db.query(Category)
        if keyword:
            query = query.filter(Category.name.ilike(f"%{keyword}%"))
            
        total = query.count()
        categories = query.offset(skip).limit(limit).all()
        return categories, total

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def create(self, category_data: dict) -> Category:
        db_category = Category(**category_data)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def update(self, category: Category, update_data: dict) -> Category:
        for key, value in update_data.items():
            setattr(category, key, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()
