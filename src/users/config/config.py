import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "user_management")

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    JWKS_URL = os.getenv("JWKS_URL", "http://localhost:5055/oauth/jkws")

    # Audit
    AUDIT_COLLECTION = "audit_logs"

    # Email / SMTP (Placeholder configs)
    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "user")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "password")

    # Service
    SERVICE_NAME = "user-management-service"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


config = Config()
