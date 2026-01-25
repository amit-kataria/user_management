from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from users.config.logging_config import get_logger

log = get_logger(__name__)


class Config(BaseSettings):
    # ----------------------------
    # MongoDB
    # ----------------------------
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "test"

    # ----------------------------
    # Redis
    # ----------------------------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # ----------------------------
    # OAuth / JWKS
    # ----------------------------
    JWKS_URL: str = "http://localhost:5055/oauth2/jwks"

    # ----------------------------
    # Audit
    # ----------------------------
    AUDIT_COLLECTION: str = "audit_logs"

    # ----------------------------
    # SMTP
    # ----------------------------
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = "user"
    SMTP_PASSWORD: str = "password"  # never printed

    # ----------------------------
    # Service
    # ----------------------------
    SERVICE_NAME: str = "user-management-service"
    ENVIRONMENT: str = "development"

    # ----------------------------
    # CORS
    # ----------------------------
    CORS_ORIGINS: List[str] = Field(default_factory=list)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_parse_delimiter = ","


def _log_env_status():
    env_path = Path(".env")
    if env_path.exists():
        log.info(".env file found and loaded")
    else:
        log.warning(".env file NOT found. Using defaults / system environment")


def _log_effective_config(cfg: Config):
    log.info("----- Application Configuration -----")
    log.info("SERVICE_NAME=%s", cfg.SERVICE_NAME)
    log.info("ENVIRONMENT=%s", cfg.ENVIRONMENT)
    log.info("MONGO_DB_NAME=%s", cfg.MONGO_DB_NAME)
    log.info("REDIS_HOST=%s", cfg.REDIS_HOST)
    log.info("REDIS_PORT=%s", cfg.REDIS_PORT)
    log.info("JWKS_URL=%s", cfg.JWKS_URL)
    log.info("AUDIT_COLLECTION=%s", cfg.AUDIT_COLLECTION)
    log.info("SMTP_HOST=%s", cfg.SMTP_HOST)
    log.info("SMTP_PORT=%s", cfg.SMTP_PORT)
    log.info("SMTP_USER=%s", cfg.SMTP_USER)
    log.info("CORS_ORIGINS=%s", cfg.CORS_ORIGINS)
    log.info("-------------------------------------")


# Instantiate once
_log_env_status()
config = Config()
_log_effective_config(config)
