from fastapi import FastAPI

from app.db.base import get_db, engine, SessionLocal
from app.models import Base
from app.routers.product_router import router as product_router
from app.routers.user_router import router as user_router_router
from app.routers.review_router import router as review_router
from app.routers.auth_router import router as auth_router
from app.routers.upload_router import router as upload_router
from app.routers.brand_router import router as brand_router
from app.routers.category_router import router as category_router
from app.routers.cart_router import router as cart_router
from app.routers.order_router import router as order_router
from app.routers.payment_router import router as payment_router
from app.models.role_model import seed_roles
from app.models.user_model import seed_admin

# Create tables and seed data on startup
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    seed_roles(db)
    seed_admin(db)
finally:
    db.close()

app = FastAPI(
    title="SHOES SHOP BABA",
    description="BABA SHOES SHOP API Documentation",
)

# CORS configuration for frontend
from app.middleware.cors import setup_cors
setup_cors(app)

app.include_router(product_router)
app.include_router(user_router_router)
app.include_router(review_router)
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(brand_router)
app.include_router(category_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(payment_router)

@app.get("/home")
async def root():
    return {"message": "Hello from BABA SHOES SHOP"}
