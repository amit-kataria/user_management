from users.repositories.role_repository import role_repo
from users.repositories.user_repository import user_repo
from users.repositories.audit_repository import audit_repo
from users.models.domain import Role, MongoRef
from users.utils.events import publish_event
from fastapi import HTTPException
from datetime import datetime
from users.config.logging_config import get_logger

log = get_logger(__name__)


class RoleService:
    async def create_role(self, role_in: Role, performed_by: str) -> Role:
        existing = await role_repo.get_by_name(role_in.name)
        if existing:
            raise HTTPException(400, "Role already exists")

        role_in.createdAt = datetime.utcnow()
        role_in.updatedAt = datetime.utcnow()
        created = await role_repo.create(role_in)
        await audit_repo.log_event("CREATE_ROLE", "roles", created.id, performed_by)
        await publish_event("role_events", "ROLE_CREATED", created.model_dump())
        return created

    async def add_permission_to_role(
        self, role_id: str, perm_ref: MongoRef, performed_by: str
    ):
        role = await role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(404, "Role not found")

        perms = role.permissions or []
        # Check duplicate
        target_oid = perm_ref.id_obj.get("$oid")
        current_oids = [p.id_obj.get("$oid") for p in perms]

        if target_oid not in current_oids:
            perms.append(perm_ref)
            await role_repo.update(
                role_id, {"permissions": [p.model_dump(by_alias=True) for p in perms]}
            )
            await audit_repo.log_event(
                "UPDATE_ROLE_PERMS",
                "roles",
                role_id,
                performed_by,
                {"added_perm": target_oid},
            )

    async def delete_role(self, role_id: str, performed_by: str):
        # Check if any users have this role in their roleIds array
        users_with_role = await user_repo.collection().count_documents(
            {"roleIds": role_id}
        )
        if users_with_role > 0:
            raise HTTPException(
                400, f"Role is assigned to {users_with_role} users, cannot delete"
            )

        await role_repo.delete(role_id)
        await audit_repo.log_event("DELETE_ROLE", "roles", role_id, performed_by)
        await publish_event("role_events", "ROLE_DELETED", {"id": role_id})

    async def get_all_roles(self):
        return await role_repo.get_all()


role_service = RoleService()
