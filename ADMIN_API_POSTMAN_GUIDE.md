# Admin API Testing Guide with Postman

## Overview

The Admin API endpoints are protected and require:
1. **Authentication** - You must be logged in (JWT token)
2. **Authorization** - Your user account must have `is_admin = true`

## Step-by-Step Instructions

### Step 1: Create an Admin User

Before you can test admin endpoints, you need to create an admin user in the database.

**Option A: Using the script (Recommended)**

```bash
# Run this from the project root directory
python scripts/create_admin.py admin@example.com YourSecurePassword123
```

This will:
- Create the database tables if they don't exist
- Create an admin user with the specified credentials
- Output the user ID and confirmation

**Option B: Manual SQL (if you have direct DB access)**

```sql
INSERT INTO users (id, email, password_hash, timezone, status, is_admin, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'admin@example.com',
    '$2b$12$...hashed_password...',  -- Use Python's get_password_hash()
    'UTC',
    'active',
    true,
    NOW(),
    NOW()
);
```

### Step 2: Login to Get JWT Token

**Request:**
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/v1/auth/login` (adjust port as needed)
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "email": "admin@example.com",
  "password": "YourSecurePassword123"
}
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "uuid-here",
    "email": "admin@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**Copy the `access_token` value** - you'll need it for the next steps.

### Step 3: Configure Authorization in Postman

For each admin endpoint request:

1. Go to the **Authorization** tab in Postman
2. Select **Type:** `Bearer Token`
3. Paste your `access_token` in the **Token** field

Alternatively, set up a **Collection Variable**:
1. Create a variable named `admin_token` at the collection level
2. Set its value to your access token
3. In each request's Authorization tab, use `{{admin_token}}` as the token

### Step 4: Test Admin Endpoints

All admin endpoints are under `/api/v1/admin/`

#### Get All Users
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/admin/users`
- **Query Params (optional):**
  - `skip`: 0 (default)
  - `limit`: 100 (default, max 500)

#### Get Single User
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/admin/users/{user_id}`
- Replace `{user_id}` with actual UUID

#### Get All User Settings
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/admin/user-settings`

#### Get All Hobbies
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/admin/hobbies`

#### Get All Coping Methods
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/admin/coping-methods`

#### Get All Emotion Records
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/admin/emotions`

#### Get All Notifications
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/admin/notifications`

#### Get All Recommendations
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/admin/recommendations`
- **Query Params (optional):**
  - `skip`: 0
  - `limit`: 100
  - `is_active`: true/false (optional filter)

#### Create Recommendation
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/v1/admin/recommendations`
- **Body (raw JSON):**
```json
{
  "trigger_type": "low_mood",
  "category": "wellness",
  "message": "Try some deep breathing exercises",
  "priority": 5,
  "is_active": true
}
```

#### Get All Subscriptions
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/admin/subscriptions`

### Step 5: Handle Common Errors

#### 401 Unauthorized
**Error:** "Not authenticated" or "Invalid or expired token"
**Solution:** 
- Your token has expired (tokens expire after 1 hour by default)
- Login again to get a fresh token
- Make sure you're using the `access_token`, not the `refresh_token`

#### 403 Forbidden
**Error:** "Доступ запрещен. Требуются права администратора." (Access denied. Admin privileges required.)
**Solution:**
- Your user doesn't have `is_admin = true`
- Run the create_admin script again with the same email - it will promote existing users to admin
- Or manually update the database: `UPDATE users SET is_admin = true WHERE email = 'admin@example.com';`

#### 404 Not Found
**Error:** "User not found" or "Recommendation not found"
**Solution:**
- The requested resource doesn't exist
- Check that the UUID is correct

## Quick Start Example Collection

Here's a ready-to-use Postman collection structure:

```
Admin API Collection
├── Variables
│   └── admin_token: (paste your token here)
├── Auth
│   └── Login (POST /api/v1/auth/login)
│       └── Tests: pm.collectionVariables.set("admin_token", pm.response.json().access_token);
├── Users
│   ├── Get All Users (GET /api/v1/admin/users)
│   ├── Get User by ID (GET /api/v1/admin/users/:user_id)
│   └── Delete User (DELETE /api/v1/admin/users/:user_id)
├── Settings
│   └── Get All Settings (GET /api/v1/admin/user-settings)
├── Hobbies
│   └── Get All Hobbies (GET /api/v1/admin/hobbies)
├── Coping Methods
│   └── Get All Coping Methods (GET /api/v1/admin/coping-methods)
├── Emotions
│   └── Get All Emotions (GET /api/v1/admin/emotions)
├── Notifications
│   └── Get All Notifications (GET /api/v1/admin/notifications)
├── Recommendations
│   ├── Get All Recommendations (GET /api/v1/admin/recommendations)
│   ├── Create Recommendation (POST /api/v1/admin/recommendations)
│   ├── Get Recommendation (GET /api/v1/admin/recommendations/:rec_id)
│   └── Delete Recommendation (DELETE /api/v1/admin/recommendations/:rec_id)
└── Subscriptions
    └── Get All Subscriptions (GET /api/v1/admin/subscriptions)
```

### Auto-Update Token Script (Optional)

Add this to your Login request's **Tests** tab to automatically save the token:

```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.collectionVariables.set("admin_token", jsonData.access_token);
    console.log("Admin token saved successfully");
}
```

Then in all admin requests, use `{{admin_token}}` in the Bearer Token field.

## Development Best Practices

1. **Never hardcode admin credentials** in your code
2. **Use environment variables** for different environments (dev, staging, prod)
3. **Rotate admin passwords** regularly in production
4. **Log admin actions** for audit trails (consider adding this feature)
5. **Use HTTPS** in production to protect tokens in transit
6. **Set appropriate token expiration** times based on security requirements

## Troubleshooting

### Database Migration Issue
If you get an error about `is_admin` column not existing:
```bash
# Run the migration
alembic upgrade head
```

### Can't Run Python Script
Make sure you have dependencies installed:
```bash
pip install -e .
# or if using poetry
poetry install
```

### Server Not Running
Start your FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
