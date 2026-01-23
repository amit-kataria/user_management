import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from users.repositories.role_repository import role_repo
from users.repositories.user_repository import user_repo
from users.models.domain import Role, User, MongoRef
from users.services.user_service import user_service
from users.utils.db import db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    print("Connecting to DB...")
    db.connect()

    roles = [
        {"name": "ROLE_ADMIN", "description": "Administrator"},
        {"name": "ROLE_ANNOTATOR", "description": "Annotator"},
        {"name": "ROLE_REVIEWER", "description": "Reviewer"},
    ]

    saved_roles = {}

    for r in roles:
        existing = await role_repo.get_by_name(r["name"])
        if not existing:
            new_role = Role(name=r["name"], description=r["description"])
            created = await role_repo.create(new_role)
            print(f"Created role: {created.name}")
            saved_roles[created.name] = created
        else:
            print(f"Role exists: {r['name']}")
            saved_roles[r["name"]] = existing

    # Create Super Admin
    admin_email = "admin@planckscale.com"
    existing_user = await user_repo.get_by_email(admin_email)

    if not existing_user:
        admin_role = saved_roles.get("ROLE_ADMIN")
        role_ref = None
        if admin_role:
            role_ref = MongoRef.from_id("roles", admin_role.id)

        user = User(
            firstName="Super",
            lastName="Admin",
            email=admin_email,
            password=pwd_context.hash("admin123"),
            tenant="default",
            enabled=True,
            confirmed=True,
            role=role_ref,
        )
        await user_repo.create(user)
        print(f"Created admin user: {admin_email}")
    else:
        print("Admin user already exists")

    db.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(seed())
