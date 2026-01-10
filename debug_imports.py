try:
    import pymysql
    print("pymysql imported")
except ImportError:
    print("pymysql NOT found")

try:
    import uvicorn
    print("uvicorn imported")
except ImportError:
    print("uvicorn NOT found")

try:
    from app.main import app
    print("app.main.app imported")
except Exception as e:
    print(f"FAILED to import app.main.app: {e}")
    import traceback
    traceback.print_exc()
