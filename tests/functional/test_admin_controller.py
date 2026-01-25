import pytest
import logging
from bson import ObjectId
from tests.utils.api_client import APIClient

logger = logging.getLogger(__name__)


class TestAdminController:
    @pytest.fixture(autouse=True)
    def setup_teardown(self, api_client: APIClient, db):
        self.created_user_ids = []
        yield
        logger.info(f"Cleaning up {len(self.created_user_ids)} users...")
        for user_id in self.created_user_ids:
            try:
                # Hard delete via DB for clean state
                db.users.delete_one({"_id": ObjectId(user_id)})
            except Exception as e:
                logger.warning(f"Failed to cleanup user {user_id}: {e}")

    def test_create_auto_confirmed_user(self, api_client):
        payload = {
            "firstName": "TestUser",
            "lastName": "AutoConfirmed",
            "email": "auto_confirmed@example.com",
            "password": "Password123!",
            "tenantId": "test-tenant",
            "roleIds": [],
            "permissionIds": [],
        }

        response = api_client.post("admins/create-user", data=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == payload["email"]
        assert "_id" in data
        assert "password" not in data
        self.created_user_ids.append(data["_id"])

    def test_get_user(self, api_client):
        # Create a user first
        payload = {
            "firstName": "TestUser",
            "lastName": "Get",
            "email": "get_user@example.com",
            "password": "Password123!",
            "tenantId": "test-tenant",
        }
        create_resp = api_client.post("admins/create-user", data=payload)
        logger.debug(f"create_resp: {create_resp.json()}")
        assert create_resp.status_code == 200
        user_id = create_resp.json()["_id"]
        self.created_user_ids.append(user_id)

        # Get the user
        response = api_client.get(f"admins/{user_id}")
        assert response.status_code == 200
        assert response.json()["_id"] == user_id

    def test_search_users(self, api_client):
        # Search for the admin user which we know exists
        payload = {"email": "test_admin@example.com"}
        response = api_client.post("admin/users/search", data=payload)
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 1
        assert users[0]["email"] == "test_admin@example.com"

    def test_update_user(self, api_client):
        # Create user
        payload = {
            "firstName": "TestUser",
            "lastName": "Update",
            "email": "update_user@example.com",
            "password": "Password123!",
            "tenantId": "test-tenant",
        }
        create_resp = api_client.post("admins/create-user", data=payload)
        user_id = create_resp.json()["_id"]
        self.created_user_ids.append(user_id)

        # Update user
        update_payload = {"firstName": "UpdatedName"}
        response = api_client.put(f"admin/user/{user_id}", data=update_payload)
        assert response.status_code == 200

        # Verify update
        get_resp = api_client.get(f"admins/{user_id}")
        assert get_resp.json()["firstName"] == "UpdatedName"

    def test_delete_user(self, api_client):
        # Create user
        payload = {
            "firstName": "TestUser",
            "lastName": "Delete",
            "email": "delete_user@example.com",
            "password": "Password123!",
            "tenantId": "test-tenant",
        }
        create_resp = api_client.post("admins/create-user", data=payload)
        user_id = create_resp.json()["_id"]
        self.created_user_ids.append(user_id)

        # Delete user
        response = api_client.delete(f"admin/user/{user_id}")
        assert response.status_code == 200

        # Verify deleted (soft)
        # Assuming search or get handles soft delete or returns it with deletedAt
        # implementation of search: "deletedAt": {"$exists": False}

        search_payload = {"email": "delete_user@example.com"}
        search_resp = api_client.post("admin/users/search", data=search_payload)
        assert search_resp.status_code == 200
        assert len(search_resp.json()) == 0
