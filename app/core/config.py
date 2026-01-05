import os
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Settings:
    SQLALCHEMY_DATABASE_URL: str = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./dev.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI")
    GOOGLE_AUTH_ENDPOINT: str = os.getenv("GOOGLE_AUTH_ENDPOINT")
    GOOGLE_TOKEN_ENDPOINT: str = os.getenv("GOOGLE_TOKEN_ENDPOINT")
    GOOGLE_USERINFO_ENDPOINT: str = os.getenv("GOOGLE_USERINFO_ENDPOINT")
    RESET_TOKEN_EXPIRE_MINUTES: int = os.getenv("RESET_TOKEN_EXPIRE_MINUTES")

    # Email settings
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", EMAIL_USERNAME)

    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET")
    
settings = Settings()
