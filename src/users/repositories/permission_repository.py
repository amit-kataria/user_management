from users.utils.db import db
from users.models.domain import Permission
from bson import ObjectId
from typing import List, Optional
from users.config.logging_config import get_logger

log = get_logger(__name__)


class PermissionRepository:
    def __init__(self):
        self.collection_name = "permissions"

    def collection(self):
        return db.get_db()[self.collection_name]

    async def create(self, perm: Permission) -> Permission:
        data = perm.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection().insert_one(data)
        perm.id = str(result.inserted_id)
        return perm

    async def get_all(self) -> List[Permission]:
        cursor = self.collection().find()
        perms = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            perms.append(Permission.model_validate(doc))
        return perms

    async def get_by_id(self, perm_id: str) -> Optional[Permission]:
        if not ObjectId.is_valid(perm_id):
            return None
        doc = await self.collection().find_one({"_id": ObjectId(perm_id)})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return Permission.model_validate(doc)

    async def delete(self, perm_id: str) -> bool:
        if not ObjectId.is_valid(perm_id):
            return False
        res = await self.collection().delete_one({"_id": ObjectId(perm_id)})
        return res.deleted_count > 0


permission_repo = PermissionRepository()
