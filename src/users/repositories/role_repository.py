from users.utils.db import db
from users.models.domain import Role
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
from users.config.logging_config import get_logger

log = get_logger(__name__)


class RoleRepository:
    def __init__(self):
        self.collection_name = "roles"

    def collection(self):
        return db.get_db()[self.collection_name]

    async def create(self, role: Role) -> Role:
        data = role.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection().insert_one(data)
        role.id = str(result.inserted_id)
        return role

    async def get_by_id(self, role_id: str) -> Optional[Role]:
        if not ObjectId.is_valid(role_id):
            return None
        doc = await self.collection().find_one({"_id": ObjectId(role_id)})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return Role.model_validate(doc)

    async def get_by_name(self, name: str) -> Optional[Role]:
        doc = await self.collection().find_one({"name": name})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return Role.model_validate(doc)

    async def get_all(self) -> List[Role]:
        cursor = self.collection().find()
        roles = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            roles.append(Role.model_validate(doc))
        return roles

    async def update(self, role_id: str, data: dict) -> bool:
        if not ObjectId.is_valid(role_id):
            return False
        data["updatedAt"] = datetime.utcnow()
        res = await self.collection().update_one(
            {"_id": ObjectId(role_id)}, {"$set": data}
        )
        return res.modified_count > 0

    async def delete(self, role_id: str) -> bool:
        if not ObjectId.is_valid(role_id):
            return False
        res = await self.collection().delete_one({"_id": ObjectId(role_id)})
        return res.deleted_count > 0


role_repo = RoleRepository()
