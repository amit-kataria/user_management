"""
Database Migration Script: roleId to roleIds
=============================================

This script migrates the User collection from single roleId to multiple roleIds.

IMPORTANT:
- Backup your database before running this script
- Test in development/staging environment first
- This script is idempotent - safe to run multiple times

Usage:
    python migrate_role_to_roles.py

Environment Variables Required:
    MONGODB_URI - MongoDB connection string
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "test")


async def migrate_users():
    """Migrate users from roleId to roleIds"""

    print(f"Connecting to MongoDB: {MONGODB_URI}")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    users_collection = db["users"]

    print(f"Connected to database: {DATABASE_NAME}")

    # Count total users
    total_users = await users_collection.count_documents({})
    print(f"Total users in database: {total_users}")

    # Find users with old roleId field
    users_with_old_schema = await users_collection.count_documents(
        {"roleId": {"$exists": True}}
    )
    print(f"Users with old roleId field: {users_with_old_schema}")

    # Find users already migrated
    users_with_new_schema = await users_collection.count_documents(
        {"roleIds": {"$exists": True}}
    )
    print(f"Users with new roleIds field: {users_with_new_schema}")

    if users_with_old_schema == 0:
        print("✓ No users need migration. All users already have roleIds field.")
        client.close()
        return

    print("\nStarting migration...")
    print("-" * 50)

    migrated_count = 0
    skipped_count = 0
    error_count = 0

    # Process each user with old schema
    cursor = users_collection.find({"roleId": {"$exists": True}})

    async for user in cursor:
        user_id = user.get("_id")
        email = user.get("email", "unknown")
        old_role_id = user.get("roleId")

        try:
            # Prepare update
            update_ops = {
                "$set": {"updatedAt": datetime.utcnow()},
                "$unset": {"roleId": ""},
            }

            # If user has a roleId, convert it to roleIds array
            if old_role_id:
                update_ops["$set"]["roleIds"] = [old_role_id]
                print(
                    f"  Migrating user: {email} - roleId: {old_role_id} → roleIds: [{old_role_id}]"
                )
            else:
                # No role, set empty array
                update_ops["$set"]["roleIds"] = []
                print(f"  Migrating user: {email} - No role → roleIds: []")

            # Perform update
            result = await users_collection.update_one({"_id": user_id}, update_ops)

            if result.modified_count > 0:
                migrated_count += 1
            else:
                skipped_count += 1
                print(f"  ⚠ User {email} was not modified (already migrated?)")

        except Exception as e:
            error_count += 1
            print(f"  ✗ Error migrating user {email}: {str(e)}")

    print("-" * 50)
    print("\nMigration Summary:")
    print(f"  ✓ Successfully migrated: {migrated_count}")
    print(f"  ⊘ Skipped (already migrated): {skipped_count}")
    print(f"  ✗ Errors: {error_count}")

    # Verify migration
    print("\nVerifying migration...")
    remaining_old_schema = await users_collection.count_documents(
        {"roleId": {"$exists": True}}
    )
    new_schema_count = await users_collection.count_documents(
        {"roleIds": {"$exists": True}}
    )

    print(f"  Users with old roleId field: {remaining_old_schema}")
    print(f"  Users with new roleIds field: {new_schema_count}")

    if remaining_old_schema == 0:
        print("\n✓ Migration completed successfully!")
    else:
        print(f"\n⚠ Warning: {remaining_old_schema} users still have old roleId field")

    client.close()


async def rollback_migration():
    """Rollback migration from roleIds to roleId (emergency use only)"""

    print("=" * 50)
    print("ROLLBACK MODE - Converting roleIds back to roleId")
    print("=" * 50)
    print("\nWARNING: This will take only the FIRST role from roleIds array!")
    print("Users with multiple roles will lose all but the first role.")

    confirm = input("\nType 'ROLLBACK' to confirm: ")
    if confirm != "ROLLBACK":
        print("Rollback cancelled.")
        return

    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    users_collection = db["users"]

    print(f"\nConnected to database: {DATABASE_NAME}")

    rollback_count = 0
    error_count = 0

    cursor = users_collection.find({"roleIds": {"$exists": True}})

    async for user in cursor:
        user_id = user.get("_id")
        email = user.get("email", "unknown")
        role_ids = user.get("roleIds", [])

        try:
            update_ops = {
                "$unset": {"roleIds": ""},
                "$set": {"updatedAt": datetime.utcnow()},
            }

            # Take first role if exists
            if role_ids and len(role_ids) > 0:
                update_ops["$set"]["roleId"] = role_ids[0]
                print(
                    f"  Rolling back user: {email} - roleIds: {role_ids} → roleId: {role_ids[0]}"
                )
            else:
                # No roles, set to None
                update_ops["$set"]["roleId"] = None
                print(f"  Rolling back user: {email} - Empty roleIds → roleId: None")

            result = await users_collection.update_one({"_id": user_id}, update_ops)

            if result.modified_count > 0:
                rollback_count += 1

        except Exception as e:
            error_count += 1
            print(f"  ✗ Error rolling back user {email}: {str(e)}")

    print("\nRollback Summary:")
    print(f"  ✓ Successfully rolled back: {rollback_count}")
    print(f"  ✗ Errors: {error_count}")

    client.close()


async def main():
    """Main function"""

    print("=" * 50)
    print("User Role Migration Tool")
    print("=" * 50)
    print("\nOptions:")
    print("1. Migrate (roleId → roleIds)")
    print("2. Rollback (roleIds → roleId)")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        await migrate_users()
    elif choice == "2":
        await rollback_migration()
    elif choice == "3":
        print("Exiting...")
    else:
        print("Invalid choice. Exiting...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nMigration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        sys.exit(1)
