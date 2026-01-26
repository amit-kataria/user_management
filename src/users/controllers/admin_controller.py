from fastapi import APIRouter, Depends, HTTPException, Body, Path
from users.utils.response_util import success_response
from users.models.domain import User, Role, Permission, MongoRef
from users.services.user_service import user_service
from users.services.role_service import role_service
from users.services.permission_service import permission_service
from users.utils.security import get_current_user, require_role
from typing import List, Dict
from users.config.logging_config import get_logger

log = get_logger(__name__)

router = APIRouter()


def get_current_sub(token_data=Depends(get_current_user)):
    # Extract sub or useful ID from token
    return token_data.get("sub", "unknown")


@router.post("/admins/create-user")
async def create_auto_confirmed_user(
    user: User, token_data=Depends(require_role("ROLE_ADMIN"))
):
    log.debug(f"create_auto_confirmed_user: {user}")
    created_by = token_data["sub"]
    tenant = token_data.get("tenantId", "")
    return success_response(
        await user_service.create_auto_confirmed_user(user, created_by, tenant),
        "User created",
    )


@router.get("/admins/{id}")
async def get_any_user(id: str, token_data=Depends(require_role("ROLE_ADMIN"))):
    log.debug(f"get_any_user: {id}")
    u = await user_service.get_user(id)
    if not u:
        raise HTTPException(404, "User not found")
    return success_response(u, "User details")


@router.post("/admin/users/search")
async def search_users(
    query: Dict = Body(...), token_data=Depends(require_role("ROLE_ADMIN"))
):
    log.debug(f"search_users: {query}")
    tenant = token_data.get("tenantId", "")
    query["tenantId"] = tenant
    return success_response(await user_service.search_users(query), "Users found")


@router.post("/admin/user")
async def invite_user(user: User, token_data=Depends(require_role("ROLE_ADMIN"))):
    log.debug(f"invite_user: {user}")
    return success_response(
        await user_service.invite_user(user, token_data["sub"]), "User invited"
    )


@router.post("/admin/user/{id}/password")
async def change_user_password(
    id: str, payload: Dict = Body(...), token_data=Depends(require_role("ROLE_ADMIN"))
):
    log.debug(f"change_user_password: {id}, {payload}")
    new_pass = payload.get("password")
    if not new_pass:
        raise HTTPException(400, "Password required")
    await user_service.change_password(id, new_pass, token_data["sub"])
    return success_response(None, "Password updated")


@router.post("/admin/user/{id}/permissions")
async def add_permission_to_user(
    id: str, perm_ref: MongoRef, token_data=Depends(require_role("ROLE_ADMIN"))
):
    log.debug(f"add_permission_to_user: {id}, {perm_ref}")
    await user_service.add_permission(id, perm_ref, token_data["sub"])
    return success_response(None, "Permission added")


@router.put("/admin/user/{id}")
async def update_user(
    id: str, payload: Dict = Body(...), token_data=Depends(require_role("ROLE_ADMIN"))
):
    log.debug(f"update_user: {id}, {payload}")
    await user_service.update_user(id, payload, token_data["sub"])
    return success_response(None, "User updated")


@router.delete("/admin/user/{id}")
async def delete_user(id: str, token_data=Depends(require_role("ROLE_ADMIN"))):
    log.debug(f"delete_user: {id}")
    await user_service.soft_delete(id, token_data["sub"])
    return success_response(None, "User deleted (soft)")


@router.delete("/admin/user/{id}/permission")
async def remove_user_permission(
    id: str,
    permission_id: str = Body(..., embed=True),
    token_data=Depends(require_role("ROLE_ADMIN")),
):
    # Note: Using Body for permission_id as typical for DELETE with payload or query param "permission_id"
    # User said "DELETE /admin/user/{id}/permission", implying payload or query. I'll support Body or move to Query if needed.
    await user_service.remove_permission(id, permission_id, token_data["sub"])
    return success_response(None, "Permission removed")


@router.post("/admin/permission")
async def create_permission(
    perm: Permission, token_data=Depends(require_role("ROLE_ADMIN"))
):
    return success_response(
        await permission_service.create_permission(perm, token_data["sub"]),
        "Permission created",
    )


@router.delete("/admin/permission")
async def delete_permission(
    id: str = Body(..., embed=True), token_data=Depends(require_role("ROLE_ADMIN"))
):
    await permission_service.delete_permission(id, token_data["sub"])
    return success_response(None, "Permission deleted")


@router.post("/admin/role")
async def create_role(role: Role, token_data=Depends(require_role("ROLE_ADMIN"))):
    return success_response(
        await role_service.create_role(role, token_data["sub"]), "Role created"
    )


@router.put("/admin/role")
async def add_permission_to_role(
    role_id: str = Body(...),
    permission: MongoRef = Body(...),
    token_data=Depends(require_role("ROLE_ADMIN")),
):
    await role_service.add_permission_to_role(role_id, permission, token_data["sub"])
    return success_response(None, "Permission added to role")


@router.delete("/admin/role")
async def delete_role(
    role_id: str = Body(..., embed=True), token_data=Depends(require_role("ROLE_ADMIN"))
):
    await role_service.delete_role(role_id, token_data["sub"])
    return success_response(None, "Role deleted")


@router.get("/admin/user/{id}")
async def get_user_admin(id: str, token_data=Depends(require_role("ROLE_ADMIN"))):
    return success_response(await user_service.get_user(id), "User details")


@router.get("/admin/roles")
async def get_roles(token_data=Depends(require_role("ROLE_ADMIN"))):
    # TODO remove super_admin from role list
    return success_response(await role_service.get_all_roles(), "Roles list")


@router.get("/admin/permissions")
async def get_permissions(token_data=Depends(require_role("ROLE_ADMIN"))):
    return success_response(await permission_service.get_all(), "Permissions list")
