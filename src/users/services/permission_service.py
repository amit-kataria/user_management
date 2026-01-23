from users.repositories.permission_repository import permission_repo
from users.repositories.audit_repository import audit_repo
from users.models.domain import Permission
from users.utils.events import publish_event
from datetime import datetime
from fastapi import HTTPException
from users.config.logging_config import get_logger

log = get_logger(__name__)


class PermissionService:
    async def create_permission(self, perm: Permission, performed_by: str):
        created = await permission_repo.create(perm)
        await audit_repo.log_event(
            "CREATE_PERMISSION", "permissions", created.id, performed_by
        )
        return created

    async def delete_permission(self, perm_id: str, performed_by: str):
        # Could also check usage in roles/users if strict integrity needed,
        # but user requirement for permission delete didn't specify strict check like Role.
        await permission_repo.delete(perm_id)
        await audit_repo.log_event(
            "DELETE_PERMISSION", "permissions", perm_id, performed_by
        )

    async def get_all(self):
        return await permission_repo.get_all()


permission_service = PermissionService()
