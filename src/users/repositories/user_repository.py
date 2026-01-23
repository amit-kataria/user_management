from users.utils.db import db
from users.models.domain import User
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
from users.config.logging_config import get_logger

log = get_logger(__name__)


class UserRepository:
    def __init__(self):
        self.collection_name = "users"

    def collection(self):
        return db.get_db()[self.collection_name]

    async def create(self, user: User) -> User:
        data = user.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection().insert_one(data)
        user.id = str(result.inserted_id)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        if not ObjectId.is_valid(user_id):
            return None
        doc = await self.collection().find_one({"_id": ObjectId(user_id)})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return User.model_validate(doc)

    async def get_by_email(self, email: str) -> Optional[User]:
        doc = await self.collection().find_one({"email": email})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return User.model_validate(doc)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        filter_query: Optional[dict] = None,
    ) -> List[User]:
        filter_query = filter_query or {}
        log.debug(f"get_all filter_query -> {filter_query}")

        cursor = self.collection().find(filter_query).skip(skip).limit(limit)
        users = []

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            users.append(User.model_validate(doc))

        return users

    async def update(self, user_id: str, update_data: dict) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        update_data["updatedAt"] = datetime.utcnow()
        res = await self.collection().update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return res.modified_count > 0

    async def soft_delete(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        update_data = {
            "deletedAt": datetime.utcnow(),
            "enabled": False,
            "attributes.status": "Deleted",
            "updatedAt": datetime.utcnow(),
        }
        res = await self.collection().update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return res.modified_count > 0

    async def ensure_indexes(self):
        await self.collection().create_index("email", unique=True)
        await self.collection().create_index("roleId")
        await self.collection().create_index("permissionIds")
        await self.collection().create_index("deletedAt", expireAfterSeconds=7776000)


user_repo = UserRepository()
