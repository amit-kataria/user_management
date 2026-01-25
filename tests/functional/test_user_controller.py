import pytest
from passlib.context import CryptContext
from tests.utils.api_client import APIClient

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestUserController:
    def test_register_user(self, anonymous_client: APIClient, db):
        payload = {
            "email": "public_register@example.com",
            "password": "Password123!",
            "firstName": "Public",
            "lastName": "User",
            "tenant": "test-tenant",
        }

        # Cleanup before
        db.users.delete_one({"email": payload["email"]})

        response = anonymous_client.post("user/register", data=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == payload["email"]

        # Cleanup
        db.users.delete_one({"email": payload["email"]})

    def test_forgot_password(self, anonymous_client: APIClient, db):
        # We need an existing user
        email = "forgot_pwd@example.com"
        db.users.delete_one({"email": email})

        # Insert user
        db.users.insert_one(
            {
                "email": email,
                "password": pwd_context.hash("Password123!"),
                "firstName": "Forgot",
                "lastName": "Pwd",
                "enabled": True,
                "confirmed": True,
                "tenantId": "test-tenant",
            }
        )

        payload = {"email": email}
        response = anonymous_client.post("user/forget", data=payload)
        assert response.status_code == 200
        assert "OTP sent" in response.json()["message"]

        # Cleanup
        db.users.delete_one({"email": email})
