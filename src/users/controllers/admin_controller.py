from fastapi import APIRouter, Depends, HTTPException, Body, Path
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


@router.post("/admins/create-user", dependencies=[Depends(require_role("ROLE_ADMIN"))])
async def create_auto_confirmed_user(user: User, sub: str = Depends(get_current_sub)):
    return await user_service.create_auto_confirmed_user(user, sub)


@router.get("/admins/{id}", dependencies=[Depends(require_role("ROLE_ADMIN"))])
async def get_any_user(id: str, sub: str = Depends(get_current_sub)):
    u = await user_service.get_user(id)
    if not u:
        raise HTTPException(404, "User not found")
    return u


@router.post("/admin/users/search")
async def search_users(query: Dict = Body(...), sub: str = Depends(get_current_sub)):
    return await user_service.search_users(query)


@router.post("/admin/user")
async def invite_user(user: User, sub: str = Depends(get_current_sub)):
    return await user_service.invite_user(user, sub)


@router.post("/admin/user/{id}/password")
async def change_user_password(
    id: str, payload: Dict = Body(...), sub: str = Depends(get_current_sub)
):
    new_pass = payload.get("password")
    if not new_pass:
        raise HTTPException(400, "Password required")
    await user_service.change_password(id, new_pass, sub)
    return {"message": "Password updated"}


@router.post("/admin/user/{id}/permissions")
async def add_permission_to_user(
    id: str, perm_ref: MongoRef, sub: str = Depends(get_current_sub)
):
    await user_service.add_permission(id, perm_ref, sub)
    return {"message": "Permission added"}


@router.put("/admin/user/{id}")
async def update_user(
    id: str, payload: Dict = Body(...), sub: str = Depends(get_current_sub)
):
    await user_service.update_user(id, payload, sub)
    return {"message": "User updated"}


@router.delete("/admin/user/{id}")
async def delete_user(id: str, sub: str = Depends(get_current_sub)):
    await user_service.soft_delete(id, sub)
    return {"message": "User deleted (soft)"}


@router.delete("/admin/user/{id}/permission")
async def remove_user_permission(
    id: str,
    permission_id: str = Body(..., embed=True),
    sub: str = Depends(get_current_sub),
):
    # Note: Using Body for permission_id as typical for DELETE with payload or query param "permission_id"
    # User said "DELETE /admin/user/{id}/permission", implying payload or query. I'll support Body or move to Query if needed.
    await user_service.remove_permission(id, permission_id, sub)
    return {"message": "Permission removed"}


@router.post("/admin/permission")
async def create_permission(perm: Permission, sub: str = Depends(get_current_sub)):
    return await permission_service.create_permission(perm, sub)


@router.delete("/admin/permission")
async def delete_permission(
    id: str = Body(..., embed=True), sub: str = Depends(get_current_sub)
):
    await permission_service.delete_permission(id, sub)
    return {"message": "Permission deleted"}


@router.post("/admin/role")
async def create_role(role: Role, sub: str = Depends(get_current_sub)):
    return await role_service.create_role(role, sub)


@router.put("/admin/role")
async def add_permission_to_role(
    role_id: str = Body(...),
    permission: MongoRef = Body(...),
    sub: str = Depends(get_current_sub),
):
    await role_service.add_permission_to_role(role_id, permission, sub)
    return {"message": "Permission added to role"}


@router.delete("/admin/role")
async def delete_role(
    role_id: str = Body(..., embed=True), sub: str = Depends(get_current_sub)
):
    await role_service.delete_role(role_id, sub)
    return {"message": "Role deleted"}


@router.get("/admin/user/{id}")
async def get_user_admin(id: str, sub: str = Depends(get_current_sub)):
    return await user_service.get_user(id)


@router.get("/admin/roles")
async def get_roles(sub: str = Depends(get_current_sub)):
    return await role_service.get_all_roles()


@router.get("/admin/permissions")
async def get_permissions(sub: str = Depends(get_current_sub)):
    return await permission_service.get_all()
