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
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection().insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        if not ObjectId.is_valid(user_id):
            return None
        doc = await self.collection().find_one({"_id": ObjectId(user_id)})
        return User(**doc) if doc else None

    async def get_by_email(self, email: str) -> Optional[User]:
        doc = await self.collection().find_one({"email": email})
        return User(**doc) if doc else None

    async def get_all(
        self, skip: int = 0, limit: int = 20, filter_query: dict = {}
    ) -> List[User]:
        cursor = self.collection().find(filter_query).skip(skip).limit(limit)
        users = []
        async for doc in cursor:
            users.append(User(**doc))
        return users

    async def update(self, user_id: str, update_data: dict) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        update_data["updatedAt"] = datetime.utcnow()
        result = await self.collection().update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def soft_delete(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        # Soft delete with 3 month retention logic handled by checking deletedAt or TTL index
        # And status update
        update_data = {
            "deletedAt": datetime.utcnow(),
            "enabled": False,
            "attributes.status": "Deleted",  # Or however we track lifecycle
            "updatedAt": datetime.utcnow(),
        }
        result = await self.collection().update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def ensure_indexes(self):
        await self.collection().create_index("email", unique=True)
        # TTL index for deletedAt
        # DB will auto-remove documents 3 months (roughly 90 days) after deletedAt
        # 90 * 24 * 60 * 60 = 7776000
        await self.collection().create_index("deletedAt", expireAfterSeconds=7776000)


user_repo = UserRepository()
