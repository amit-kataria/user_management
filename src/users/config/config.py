from typing import List
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "test"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    JWKS_URL: str = "http://localhost:5055/oauth2/jwks"

    # Audit
    AUDIT_COLLECTION: str = "audit_logs"

    # Email / SMTP (Placeholder configs)
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = "user"
    SMTP_PASSWORD: str = "password"

    # Service
    SERVICE_NAME: str = "user-management-service"
    ENVIRONMENT: str = "development"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]


config = Config()
