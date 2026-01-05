# app/db/init_db.py
from sqlalchemy.orm import Session
from app.db.base import SessionLocal, engine
from app.models.base_model import Base
from app.models.role_model import Role

def seed_roles(db: Session):
    """Seed initial roles"""
    existing_roles = db.query(Role).count()
    
    if existing_roles == 0:
        roles = [
            Role(id=1, name="admin", description="Administrator with full access"),
            Role(id=2, name="user", description="Regular user with limited access")
        ] 
        
        db.add_all(roles)
        db.commit()
        print("✓ Roles seeded successfully!")
    else:
        print("✓ Roles already exist, skipping seed.")

def init_db():
    """Initialize database: create tables and seed data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created!")
    
    # Seed roles
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()

if __name__ == "__main__":
    init_db()