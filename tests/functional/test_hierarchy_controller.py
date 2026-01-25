import pytest
from tests.utils.api_client import APIClient


class TestHierarchyController:
    @pytest.fixture(autouse=True)
    def setup_hierarchy_data(self, db):
        # Create roles
        if not db.roles.find_one({"name": "ROLE_ANNOTATOR"}):
            db.roles.insert_one({"name": "ROLE_ANNOTATOR"})
        if not db.roles.find_one({"name": "ROLE_REVIEWER"}):
            db.roles.insert_one({"name": "ROLE_REVIEWER"})

        annotator_role_id = str(db.roles.find_one({"name": "ROLE_ANNOTATOR"})["_id"])
        reviewer_role_id = str(db.roles.find_one({"name": "ROLE_REVIEWER"})["_id"])

        # Create users
        # Note: We need password for validation if strictly required, but usually search ignores password
        users = [
            {
                "email": "h_annotator@test.com",
                "password": "x",
                "roleIds": [annotator_role_id],
                "tenantId": "h-tenant",
                "enabled": True,
                "confirmed": True,
                "firstName": "A",
                "lastName": "A",
            },
            {
                "email": "h_reviewer@test.com",
                "password": "x",
                "roleIds": [reviewer_role_id],
                "tenantId": "h-tenant",
                "enabled": True,
                "confirmed": True,
                "firstName": "R",
                "lastName": "R",
            },
            {
                "email": "h_other@test.com",
                "password": "x",
                "roleIds": [],
                "tenantId": "h-tenant",
                "enabled": True,
                "confirmed": True,
                "firstName": "O",
                "lastName": "O",
            },
        ]

        self.created_emails = [u["email"] for u in users]

        # Cleanup first just in case
        db.users.delete_many({"email": {"$in": self.created_emails}})

        for u in users:
            db.users.insert_one(u)

        yield

        # Cleanup
        db.users.delete_many({"email": {"$in": self.created_emails}})

    def test_get_all_active_users(self, api_client):
        response = api_client.get("hierarchy/tenant/h-tenant/users")
        assert response.status_code == 200
        users = response.json()

        emails = [u["email"] for u in users]
        assert "h_annotator@test.com" in emails
        assert "h_reviewer@test.com" in emails
        assert "h_other@test.com" in emails

    def test_get_users_by_role(self, api_client):
        response = api_client.get("hierarchy/tenant/h-tenant/users/ROLE_ANNOTATOR")
        assert response.status_code == 200
        users = response.json()
        emails = [u["email"] for u in users]
        assert "h_annotator@test.com" in emails
        assert "h_reviewer@test.com" not in emails
