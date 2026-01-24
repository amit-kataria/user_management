# Hierarchy API Quick Reference

## Base URL
```
http://localhost:5403
```

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Get Users by Role Type

**Endpoint**: `GET /hierarchy/tenant/{tenantId}/users/{role_type}`

**Description**: Retrieve all active and confirmed users with a specific role in a tenant.

**Path Parameters**:
- `tenantId` (string, required): The tenant identifier (e.g., "LAWCO")
- `role_type` (string, required): The role name (e.g., "ROLE_ANNOTATOR", "ROLE_REVIEWER")

**Query Parameters**: None

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Success Response** (200 OK):
```json
[
  {
    "_id": "68f8730275e2e6d7ce1df373",
    "firstName": "Arjun",
    "lastName": "Sharma",
    "email": "arjun.sharma@example.com",
    "tenantId": "LAWCO",
    "phoneNumber": "9810155501",
    "enabled": true,
    "confirmed": true,
    "roleIds": ["68f50152de15e60dfd620d0a"],
    "permissionIds": ["68f50153de15e60dfd620d13"],
    "attributes": {},
    "createdAt": "2025-11-24T06:37:38.844Z",
    "updatedAt": "2025-11-24T06:37:38.844Z"
  }
]
```

**Error Responses**:
- `404 Not Found`: Role type not found
  ```json
  {
    "detail": "Role 'ROLE_ANNOTATOR' not found"
  }
  ```
- `401 Unauthorized`: Invalid or missing JWT token

**Example cURL**:
```bash
curl -X GET \
  "http://localhost:5403/hierarchy/tenant/LAWCO/users/ROLE_ANNOTATOR" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Example Python**:
```python
import requests

url = "http://localhost:5403/hierarchy/tenant/LAWCO/users/ROLE_ANNOTATOR"
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
users = response.json()
```

---

### 2. Get All Active Users

**Endpoint**: `GET /hierarchy/tenant/{tenantId}/users`

**Description**: Retrieve all active users in a tenant, regardless of their role.

**Path Parameters**:
- `tenantId` (string, required): The tenant identifier (e.g., "LAWCO")

**Query Parameters**: None

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Success Response** (200 OK):
```json
[
  {
    "_id": "68f8730275e2e6d7ce1df373",
    "firstName": "Arjun",
    "lastName": "Sharma",
    "email": "arjun.sharma@example.com",
    "tenantId": "LAWCO",
    "phoneNumber": "9810155501",
    "enabled": true,
    "confirmed": true,
    "roleIds": ["68f50152de15e60dfd620d0a"],
    "permissionIds": ["68f50153de15e60dfd620d13"],
    "attributes": {},
    "createdAt": "2025-11-24T06:37:38.844Z",
    "updatedAt": "2025-11-24T06:37:38.844Z"
  },
  {
    "_id": "68f8730275e2e6d7ce1df374",
    "firstName": "Priya",
    "lastName": "Patel",
    "email": "priya.patel@example.com",
    "tenantId": "LAWCO",
    "phoneNumber": "9810155502",
    "enabled": true,
    "confirmed": false,
    "roleIds": ["68f50152de15e60dfd620d0b"],
    "permissionIds": [],
    "attributes": {},
    "createdAt": "2025-11-24T07:15:22.123Z",
    "updatedAt": "2025-11-24T07:15:22.123Z"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing JWT token

**Example cURL**:
```bash
curl -X GET \
  "http://localhost:5403/hierarchy/tenant/LAWCO/users" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Example Python**:
```python
import requests

url = "http://localhost:5403/hierarchy/tenant/LAWCO/users"
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
users = response.json()
```

**Example JavaScript (Fetch)**:
```javascript
const tenantId = 'LAWCO';
const url = `http://localhost:5403/hierarchy/tenant/${tenantId}/users`;

fetch(url, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
})
  .then(response => response.json())
  .then(users => console.log(users))
  .catch(error => console.error('Error:', error));
```

---

## Common Role Types

Based on typical user management systems, here are common role types you might use:

- `ROLE_USER` - Default user role
- `ROLE_ADMIN` - Administrator role
- `ROLE_ANNOTATOR` - Annotator role (for annotation tasks)
- `ROLE_REVIEWER` - Reviewer role (for reviewing annotations)
- `ROLE_MANAGER` - Manager role
- `ROLE_SUPERVISOR` - Supervisor role

**Note**: The actual role names depend on what's configured in your `roles` collection in MongoDB.

---

## Filtering Logic

### Endpoint 1 (By Role Type)
Filters applied:
- `tenantId` = specified tenant
- `enabled` = true
- `confirmed` = true
- `roleIds` contains the ID of the specified role type
- `deletedAt` does not exist (excludes soft-deleted users)

### Endpoint 2 (All Active Users)
Filters applied:
- `tenantId` = specified tenant
- `enabled` = true
- `deletedAt` does not exist (excludes soft-deleted users)

**Note**: Endpoint 2 includes both confirmed and unconfirmed users, as long as they are enabled.

---

## Response Limits

Currently, both endpoints return up to 1000 users. For production use with large datasets, consider implementing pagination.

---

## Testing with Swagger/OpenAPI

The API documentation is available at:
```
http://localhost:5403/docs
```

You can test the endpoints interactively using the Swagger UI.
