from users.utils.db import db
from users.models.domain import AuditLog
from datetime import datetime
from users.config.logging_config import get_logger

log = get_logger(__name__)


class AuditRepository:
    def __init__(self):
        self.collection_name = "audit_logs"

    async def log_event(
        self,
        action: str,
        target_collection: str,
        target_id: str,
        performed_by: str,
        details: dict = None,
    ):
        try:
            log = AuditLog(
                action=action,
                target_collection=target_collection,
                target_id=str(target_id),
                performed_by=performed_by,
                details=details or {},
            )
            await db.get_db()[self.collection_name].insert_one(log.model_dump())
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")


audit_repo = AuditRepository()
