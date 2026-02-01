from ast import Dict
from ast import Tuple
from users.services.role_service import role_service
from fastapi import UploadFile
from users.repositories.user_repository import user_repo
from users.repositories.audit_repository import audit_repo
from users.models.domain import User, MongoRef
from users.utils.events import publish_event
from users.services import otp_service, email_service
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime
from typing import Optional, List
from users.config.logging_config import get_logger
import io
import csv

log = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    async def get_user(self, user_id: str) -> Optional[User]:
        return await user_repo.get_by_id(user_id)

    async def create_auto_confirmed_user(
        self, user_in: User, performed_by: str, tenant: str
    ) -> User:
        existing = await user_repo.get_by_email(user_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")

        user_in.password = pwd_context.hash(user_in.password)
        user_in.enabled = True
        user_in.confirmed = True
        user_in.createdBy = performed_by
        user_in.createdAt = datetime.utcnow()
        user_in.updatedAt = datetime.utcnow()
        user_in.tenantId = tenant

        created = await user_repo.create(user_in)
        log.debug(f"created user {created}")
        await audit_repo.log_event("CREATE_USER", "users", created.id, performed_by)
        await publish_event("user_events", "USER_CREATED", created.model_dump())
        return created

    async def register_user_self(
        self, email: str, password: str, first_name: str, last_name: str, tenant: str
    ) -> User:
        existing = await user_repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")

        otp = await otp_service.generate_otp(email)
        await email_service.send_otp_email(email, otp)

        new_user = User(
            firstName=first_name,
            lastName=last_name,
            email=email,
            password=pwd_context.hash(password),
            tenantId=tenant,
            confirmed=False,
            enabled=True,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow(),
            # role should be DEFAULT role, handled by caller or defaults
        )
        created = await user_repo.create(new_user)
        await audit_repo.log_event("REGISTER_SELF", "users", created.id, "SELF")
        return created

    async def confirm_user(self, email: str, otp: str):
        valid = await otp_service.verify_otp(email, otp)
        if not valid:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        user = await user_repo.get_by_email(email)
        if not user:
            raise HTTPException(404, "User not found")

        await user_repo.update(
            user.id, {"confirmed": True, "attributes.status": "Active"}
        )
        await audit_repo.log_event("CONFIRM_USER", "users", user.id, "SELF")
        await publish_event("user_events", "USER_CONFIRMED", {"id": user.id})
        return True

    async def change_password(self, user_id: str, new_password: str, performed_by: str):
        hashed = pwd_context.hash(new_password)
        await user_repo.update(user_id, {"password": hashed, "updatedBy": performed_by})
        await audit_repo.log_event("CHANGE_PASSWORD", "users", user_id, performed_by)
        await publish_event("user_events", "USER_PASSWORD_CHANGED", {"id": user_id})

    async def update_user(self, user_id: str, update_data: dict, performed_by: str):
        # Remove protected fields if any?
        # For now trust admin
        update_data["updatedBy"] = performed_by
        success = await user_repo.update(user_id, update_data)
        if success:
            await audit_repo.log_event(
                "UPDATE_USER", "users", user_id, performed_by, update_data
            )
            await publish_event(
                "user_events", "USER_UPDATED", {"id": user_id, "changes": update_data}
            )
        return success

    async def search_users(self, query: dict) -> List[User]:
        mongo_filter = {}
        if "name" in query and query["name"]:
            mongo_filter["$or"] = [
                {"firstName": {"$regex": query["name"], "$options": "i"}},
                {"lastName": {"$regex": query["name"], "$options": "i"}},
            ]
        if "tenantId" in query and query["tenantId"]:
            mongo_filter["tenantId"] = query["tenantId"]
        if "roleIds" in query and query["roleIds"]:
            # Needs careful handling of mongo ref if query is by role name vs role ID
            mongo_filter["roleIds"] = {"$in": [query["roleIds"]]}
        if "enabled" in query and query["enabled"]:
            mongo_filter["enabled"] = query["enabled"]
        if "confirmed" in query and query["confirmed"]:
            mongo_filter["confirmed"] = query["confirmed"]
        if "email" in query and query["email"]:
            mongo_filter["email"] = query["email"]
        mongo_filter["deletedAt"] = {"$exists": False}

        log.debug(f"search_users mongo_filter -> {mongo_filter}")
        return await user_repo.get_all(filter_query=mongo_filter)

    async def invite_user(self, user_in: User, performed_by: str) -> User:
        # Create unconfirmed, send email with set password or OTP link?
        # Requirement: "user will enter email flow" -> "create/invite a user, ... then user has to enter otp received in email"
        # So it's like Register but initiated by Admin.
        existing = await user_repo.get_by_email(user_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")

        # Generate OTP
        otp = await otp_service.generate_otp(user_in.email)
        await email_service.send_otp_email(user_in.email, otp)

        user_in.password = pwd_context.hash(
            user_in.password
        )  # Temporary password? Or random?
        user_in.confirmed = False
        user_in.createdBy = performed_by
        created = await user_repo.create(user_in)

        await audit_repo.log_event("INVITE_USER", "users", created.id, performed_by)
        return created

    async def soft_delete(self, user_id: str, performed_by: str):
        await user_repo.soft_delete(user_id)
        await audit_repo.log_event("DELETE_USER", "users", user_id, performed_by)
        await publish_event("user_events", "USER_DELETED", {"id": user_id})

    async def add_permission(
        self, user_id: str, permission_ref: MongoRef, performed_by: str
    ):
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        current_perms = user.permissions or []
        current_ids = [p.id_obj.get("$oid") for p in current_perms]
        new_oid = permission_ref.id_obj.get("$oid")

        if new_oid not in current_ids:
            current_perms.append(permission_ref)
            await user_repo.update(
                user_id,
                {"permissions": [p.model_dump(by_alias=True) for p in current_perms]},
            )
            await audit_repo.log_event(
                "ADD_USER_PERMISSION",
                "users",
                user_id,
                performed_by,
                {"permission": new_oid},
            )

    async def remove_permission(
        self, user_id: str, permission_id: str, performed_by: str
    ):
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        current_perms = user.permissions or []
        new_perms = [p for p in current_perms if p.id_obj.get("$oid") != permission_id]

        if len(new_perms) != len(current_perms):
            await user_repo.update(
                user_id,
                {"permissions": [p.model_dump(by_alias=True) for p in new_perms]},
            )
            await audit_repo.log_event(
                "REMOVE_USER_PERMISSION",
                "users",
                user_id,
                performed_by,
                {"permission": permission_id},
            )

    async def bulk_invite_users(
        self,
        file: UploadFile,
        tenant_id: str,
        performed_by: str,
    ) -> tuple[int, list[dict]]:
        content = await file.read()

        stream = io.StringIO(content.decode("utf-8"))
        reader = csv.DictReader(stream)

        roles = await role_service.get_all_roles()
        role_map = {r.name.lower(): str(r.id) for r in roles}
        # Also support mapping without ROLE_ prefix
        role_map.update({r.name.lower().replace("role_", ""): str(r.id) for r in roles})

        success_count = 0
        errors = []

        for row in reader:
            try:
                # Expected headers: FirstName, LastName, Email, PhoneNumber, Role
                first_name = row.get("FirstName")
                last_name = row.get("LastName")
                email = row.get("Email")
                phone = row.get("PhoneNumber")
                role_name = row.get("Role", "").lower()

                if not email or not first_name:
                    raise ValueError(f"Missing required fields for row: {row}")

                role_id = role_map.get(role_name)
                if not role_id:
                    log.warning(
                        f"Role {role_name} not found, using default if applicable"
                    )
                    # You might want to skip or use a default role. Let's error for clarity.
                    # raise ValueError(f"Role {role_name} is invalid")

                user_in = User(
                    firstName=first_name,
                    lastName=last_name or "",
                    email=email,
                    phone=phone,
                    tenantId=tenant_id,
                    roleIds=[role_id] if role_id else [],
                    password="ChangeMe123!",  # Should probably be random or handled by invite flow
                    enabled=True,
                    confirmed=False,
                )

                await user_service.invite_user(user_in, performed_by)
                success_count += 1
            except Exception as e:
                log.error(f"Error inviting user {row.get('Email')}: {str(e)}")
                errors.append({"email": row.get("Email"), "error": str(e)})
        return success_count, errors


user_service = UserService()
