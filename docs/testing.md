# Architecture

The testing implementation follows a modular structure:

1.  **tests/utils/api_client.py**: A **RestAssured-like** wrapper around 

    *requests*

    . It handles:

    - Base URLs and Authentication headers.

    - Automatic request/response logging (JSON bodies, params, etc.).

    - Simplified HTTP methods (get, post, put, delete).

2.  **tests/conftest.py**: The pytest configuration file containing robust fixtures:

    - setup_data: Idempotently creates a test **OAuth2 Client**, **Admin Role**, and **Admin User** in MongoDB at the start of the session and cleans them up at the end.

    - admin_token: Automatically authenticates with 

      *oauth2_login_server*

       to retrieve a valid JWT for testing.

    - api_client: Provides an authenticated instance of 

      APIClient to your tests.

    - db: Provides a direct MongoDB connection for data setup and hard-cleanup.

3.  *****tests/functional/*****

    : Contains the actual test cases, organized by controller.

# Created Files

*user_management/*

- *tests/config/settings.py*

   (Configuration for URLs and DB)

- *tests/utils/api_client.py*

   (The test library)

- *tests/conftest.py*

   (Fixtures and boilerplate)

- *tests/functional/test_admin_controller.py*

- *tests/functional/test_user_controller.py*

- *tests/functional/test_hierarchy_controller.py*

# How to Run

Prerequisites: Ensure *oauth2_login_server* (port 5055), *user_management* (port 5403), and MongoDB (port 27017) are running.

Install the test dependencies:

```bash
pip install pytest requests pymongo passlib
```
To run the tests:

```bash
pytest tests
```
# Key Features Implemented

- **Automatic Auth**: The tests automatically fetch a real token from the OAuth2 server.

- **Residue Cleanup**:

  - The **Session** fixture cleans up the test admin user and client after the entire suite finishes.

  - **Functional Tests** (e.g., 

    *test_admin_controller.py*

    ) track created resources and perform a **Hard Delete** directly via MongoDB in the teardown phase to ensure no soft-deleted \"residue\" remains.

- **Logging**: All API requests and responses are logged to the console for easy debugging.
