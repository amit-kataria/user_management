from pymongo import MongoClient
from bson import DBRef, ObjectId
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("rollback")

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "user_management"
USERS_COLLECTION = "users"


def rollback():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users = db[USERS_COLLECTION]

    count = 0

    for user in users.find({}):
        updates = {}
        unset = {}

        # --- roleId -> role (DBRef) ---
        role_id = user.get("roleId")
        if role_id and "role" not in user:
            try:
                updates["role"] = DBRef("roles", ObjectId(role_id))
                unset["roleId"] = ""
            except Exception:
                log.warning(f"Invalid roleId for user {user['_id']}: {role_id}")

        # --- permissionIds -> permissions (DBRef list) ---
        perm_ids = user.get("permissionIds", [])
        if perm_ids and "permissions" not in user:
            refs = []
            for pid in perm_ids:
                try:
                    refs.append(DBRef("permissions", ObjectId(pid)))
                except Exception:
                    log.warning(
                        f"Invalid permissionId for user {user['_id']}: {pid}"
                    )
            if refs:
                updates["permissions"] = refs
                unset["permissionIds"] = ""

        if updates or unset:
            _id = user["_id"]
            log.info(f"Rolling back user {_id}")

            update_doc = {}
            if updates:
                update_doc["$set"] = updates
            if unset:
                update_doc["$unset"] = unset

            users.update_one({"_id": _id}, update_doc)
            count += 1

    log.info(f"Rollback complete. Updated {count} users.")


if __name__ == "__main__":
    rollback()
