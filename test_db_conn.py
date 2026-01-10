from app.db.base import engine, SessionLocal
from sqlalchemy import text

print("Testing database connection...")
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection success:", result.fetchone())
except Exception as e:
    print("Database connection failed:", e)
