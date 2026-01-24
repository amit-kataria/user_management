from fastapi import APIRouter, Depends, HTTPException, Path
from users.models.domain import User
from users.repositories.user_repository import user_repo
from users.repositories.role_repository import role_repo
from users.services.user_service import user_service
from users.utils.security import validate_token
from typing import List
from users.config.logging_config import get_logger

log = get_logger(__name__)

router = APIRouter()


@router.get("/hierarchy/tenant/{tenantId}/users/{role_type}", response_model=List[User])
async def get_users_by_role(
    tenantId: str = Path(..., description="Tenant ID"),
    role_type: str = Path(
        ..., description="Role type (e.g., ROLE_ANNOTATOR, ROLE_REVIEWER)"
    ),
    token_data=Depends(validate_token),
):
    """
    Get all active and confirmed users who have a specific role type.
    This is a multi-tenant implementation.

    Args:
        tenantId: The tenant ID to filter users
        role_type: The role type to filter users (e.g., ROLE_ANNOTATOR, ROLE_REVIEWER)
        token_data: JWT token data from authentication

    Returns:
        List of users matching the criteria
    """
    log.info(f"Fetching users for tenant: {tenantId}, role: {role_type}")

    # First, get the role by name to get its ID
    role = await role_repo.get_by_name(role_type)
    if not role:
        log.warning(f"Role not found: {role_type}")
        raise HTTPException(status_code=404, detail=f"Role '{role_type}' not found")

    # Build the filter query for active, confirmed users with the specific role
    filter_query = {
        "tenantId": tenantId,
        "enabled": True,
        "confirmed": True,
        "roleIds": role.id,  # MongoDB will match if role.id is in the roleIds array
        "deletedAt": {"$exists": False},  # Exclude soft-deleted users
    }

    log.debug(f"Filter query: {filter_query}")
    users = await user_service.search_users(filter_query=filter_query)

    # Fetch users matching the criteria
    # users = await user_repo.get_all(filter_query=filter_query, limit=1000)

    log.info(f"Found {len(users)} users for tenant {tenantId} with role {role_type}")

    return users


@router.get("/hierarchy/tenant/{tenantId}/users", response_model=List[User])
async def get_all_active_users(
    tenantId: str = Path(..., description="Tenant ID"),
    token_data=Depends(validate_token),
):
    """
    Get all active users in the tenant, regardless of their role.
    This is a multi-tenant implementation.

    Args:
        tenantId: The tenant ID to filter users
        token_data: JWT token data from authentication

    Returns:
        List of all active users in the tenant
    """
    log.info(f"Fetching all active users for tenant: {tenantId}")

    # Build the filter query for active users
    filter_query = {
        "tenantId": tenantId,
        "enabled": True,
        "deletedAt": {"$exists": False},  # Exclude soft-deleted users
    }

    log.debug(f"Filter query: {filter_query}")
    users = await user_service.search_users(filter_query=filter_query)

    # Fetch users matching the criteria
    # users = await user_repo.get_all(filter_query=filter_query, limit=1000)

    log.info(f"Found {len(users)} active users for tenant {tenantId}")

    return users
