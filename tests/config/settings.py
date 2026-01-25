import os


class TestSettings:
    USER_MGMT_URL = os.getenv("USER_MGMT_URL", "http://localhost:5403")
    OAUTH2_URL = os.getenv("OAUTH2_URL", "http://localhost:5055")

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "test")

    TEST_CLIENT_ID = "test-client-id"
    TEST_CLIENT_SECRET = "test-client-secret"

    ADMIN_EMAIL = "test_admin@example.com"
    ADMIN_PASSWORD = "Password123!"

    DEFAULT_TENANT_ID = "test-tenant"


settings = TestSettings()
