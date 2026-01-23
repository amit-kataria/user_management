from pymongo import MongoClient
from bson import DBRef, ObjectId
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("migration")

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "test"
USERS_COLLECTION = "users"


def extract_oid(v):
    if isinstance(v, DBRef):
        return str(v.id)
    return None


def migrate():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users = db[USERS_COLLECTION]

    count = 0

    for user in users.find({}):
        updates = {}
        unset = {}

        # --- role ---
        role = user.get("role")
        if isinstance(role, DBRef):
            updates["roleId"] = str(role.id)
            unset["role"] = ""

        # --- permissions ---
        permissions = user.get("permissions", [])
        if permissions and all(isinstance(p, DBRef) for p in permissions):
            updates["permissionIds"] = [str(p.id) for p in permissions]
            unset["permissions"] = ""

        if updates or unset:
            _id = user["_id"]
            log.info(f"Migrating user {_id}")
            update_doc = {}
            if updates:
                update_doc["$set"] = updates
            if unset:
                update_doc["$unset"] = unset

            users.update_one({"_id": _id}, update_doc)
            count += 1

    log.info(f"Migration complete. Updated {count} users.")


if __name__ == "__main__":
    migrate()
