# User Management Service (Python V2)

New backend implementation in Python 3.9 using FastAPI, MongoDB, and Redis.
Replaces the legacy Java implementation.

## Tech Stack
- **Language**: Python 3.9
- **Framework**: FastAPI
- **Database**: MongoDB (Motor async driver)
- **Cache/Streams**: Redis
- **Security**: JWT validation (JWKS)

## Structure
- `src/users/`: Main application code
  - `controllers/`: API Endpoints
  - `services/`: Business Logic
  - `repositories/`: Data Access & Audit
  - `models/`: Pydantic Schemas
  - `config/`: Environment Configuration

## Setup

1. **Prerequisites**: Python 3.9+, MongoDB, Redis.

2. **Install Dependencies**:
   ```bash
   pip install -e .
   ```

3. **Environment**:
   Create `.env` file with:
   ```env
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB_NAME=user_management
   REDIS_HOST=localhost
   REDIS_PORT=6379
   JWKS_URL=http://localhost:5055/oauth/jkws
   ```

4. **Run**:
   ```bash
   uvicorn src.users.main:app --reload
   ```

## API Documentation
The API docs are available at `http://localhost:8000/docs` once running.