import pytest
from pymongo import MongoClient
from passlib.context import CryptContext
from tests.config.settings import settings
from tests.utils.api_client import APIClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="session")
def db_client():
    client = MongoClient(settings.MONGO_URI)
    yield client
    client.close()


@pytest.fixture(scope="session")
def db(db_client):
    return db_client[settings.DB_NAME]


@pytest.fixture(scope="session")
def setup_data(db):
    """
    Sets up initial data:
    1. OAuth2 Client
    2. Admin Role
    3. Admin User
    """
    logger.info("Setting up test data...")
    # 1. OAuth2 Client
    client_coll = db["oauth2_clients"]
    client_coll.delete_one({"client_id": settings.TEST_CLIENT_ID})

    hashed_secret = pwd_context.hash(settings.TEST_CLIENT_SECRET)

    client_data = {
        "client_id": settings.TEST_CLIENT_ID,
        "client_secret": hashed_secret,
        "grant_types": [
            "password",
            "refresh_token",
            "client_credentials",
            "authorization_code",
        ],
        "redirect_uris": ["http://localhost:3000/callback"],
        "response_types": ["code", "token"],
        "scope": "openid profile email",
        "default_scopes": ["openid", "profile", "email"],
        "name": "Test Client",
    }
    client_coll.insert_one(client_data)

    # 2. Admin Role
    role_coll = db["roles"]
    admin_role = role_coll.find_one({"name": "ROLE_ADMIN"})
    if not admin_role:
        result = role_coll.insert_one(
            {
                "name": "ROLE_ADMIN",
                "description": "Administrator Role",
                "isDefault": False,
                "permissionIds": [],
            }
        )
        role_id = str(result.inserted_id)
    else:
        role_id = str(admin_role["_id"])

    # 3. Admin User
    user_coll = db["users"]
    user_coll.delete_one({"email": settings.ADMIN_EMAIL})

    hashed_password = pwd_context.hash(settings.ADMIN_PASSWORD)

    user_data = {
        "firstName": "Test",
        "lastName": "Admin",
        "email": settings.ADMIN_EMAIL,
        "password": hashed_password,
        "enabled": True,
        "confirmed": True,
        "tenantId": settings.DEFAULT_TENANT_ID,
        "roleIds": [role_id],
        "permissionIds": [],
    }
    user_coll.insert_one(user_data)

    yield

    logger.info("Cleaning up test data...")
    user_coll.delete_one({"email": settings.ADMIN_EMAIL})
    client_coll.delete_one({"client_id": settings.TEST_CLIENT_ID})


@pytest.fixture(scope="session")
def admin_token(setup_data):
    """
    Authenticates and returns the access token.
    """
    # Use APIClient to call OAuth2 Server
    client = APIClient(settings.OAUTH2_URL)

    # Password flow
    payload = {
        "grant_type": "password",
        "client_id": settings.TEST_CLIENT_ID,
        "client_secret": settings.TEST_CLIENT_SECRET,
        "username": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD,
    }

    logger.info("Fetching admin token...")
    # Since OAuth2 server expects Form data for token endpoint usually, but let's check oauth2_controller.
    # It says: grant_type: str = Form(...), code: str = Form("")...
    # So we should send as form data usually.
    # However, requests `data` param sends form-urlencoded by default if it's a dict.
    # APIClient.post uses `json=data` if it's a dict unless I changed it.
    # Let's check APIClient.request.
    # It does:
    # if data is not None and isinstance(data, (dict, list)): json_data = data; data = None
    # This sends JSON.
    # But OAuth2 spec requires application/x-www-form-urlencoded.
    # I need to fix APIClient or override here.

    # I'll manually send data and header for this request.
    import requests

    response = requests.post(
        f"{settings.OAUTH2_URL}/oauth2/token",
        data=payload,  # This sends form-urlencoded
        headers={"Accept": "application/json"},
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get token: {response.text}")

    return response.json()["access_token"]


@pytest.fixture(scope="function")
def api_client(admin_token):
    return APIClient(settings.USER_MGMT_URL, token=admin_token)


@pytest.fixture(scope="function")
def anonymous_client():
    return APIClient(settings.USER_MGMT_URL)
