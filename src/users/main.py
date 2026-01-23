from users.utils.security import jwks_cache
from users.config.logging_config import setup_logging, get_logger

setup_logging()
log = get_logger(__name__)

from fastapi import FastAPI
from users.config.config import config
from users.utils.db import db
from users.utils.redis_client import redis_client
from users.controllers import admin_controller, user_controller
import sys
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="User Management Service", version="1.0.0")


@app.on_event("startup")
async def startup_event():
    log.info("Starting up User Management Service")
    db.connect()
    try:
        from users.repositories.user_repository import user_repo

        await user_repo.ensure_indexes()
        # jwks_cache.start_jwks_refresh()
    except Exception as e:
        log.error(f"Index creation failed: {e}")

    await redis_client.connect()


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down User Management Service")
    db.close()
    await redis_client.close()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(admin_controller.router, tags=["Admin"])
app.include_router(user_controller.router, tags=["User"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": config.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn

    log.info(f"Starting Uvicorn server...")
    try:
        uvicorn.run(
            "users.main:app", host="0.0.0.0", port=5403, reload=False, log_level="info"
        )
    except Exception as e:
        log.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)
