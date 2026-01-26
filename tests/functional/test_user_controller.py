import pytest
from passlib.context import CryptContext
from tests.utils.api_client import APIClient

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
test_email = "amit2.kataria@gmail.com"


class TestUserController:
    def test_register_user(self, anonymous_client: APIClient, db):
        payload = {
            "email": test_email,
            "password": "Password123!",
            "firstName": "Public",
            "lastName": "User",
            "tenantId": "self",
        }

        # Cleanup before
        db.users.delete_one({"email": payload["email"]})

        response = anonymous_client.post("user/register", data=payload)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["email"] == payload["email"]

        # Cleanup
        db.users.delete_one({"email": payload["email"]})

    def test_forgot_password(self, anonymous_client: APIClient, db):
        # We need an existing user
        email = test_email
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
                "tenantId": "self",
            }
        )

        payload = {"email": email}
        response = anonymous_client.post("user/forget", data=payload)
        assert response.status_code == 200
        assert "OTP sent" in response.json()["message"]

        # Cleanup
        db.users.delete_one({"email": email})
