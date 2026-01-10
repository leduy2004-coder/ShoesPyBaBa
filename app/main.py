from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for error in exc.errors():
        loc = error.get("loc")
        msg = error.get("msg")
        field = loc[-1] if loc else "field"
        error_messages.append(f"{field}: {msg}")
    
    full_message = " | ".join(error_messages)
    return JSONResponse(
        status_code=200,
        content={
            "code": "422",
            "message": full_message,
            "data": None
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": str(exc.status_code),
            "message": exc.detail,
            "data": None
        }
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
