from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import get_db, engine, SessionLocal
from app.models import Base
from app.routers.product_router import router as product_router
from app.routers.user_router import router as user_router_router
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        # Add your frontend URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(user_router_router)

@app.get("/home")
async def root():
    return {"message": "Hello from BABA SHOES SHOP"}
