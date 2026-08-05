# CIVIC GO AI - API

FastAPI backend with PostgreSQL, JWT authentication, Argon2 password hashing, and Alembic migrations.

## Quick start

1. Create and activate a virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Create your configuration: `cp .env.example .env`, then set a strong `JWT_SECRET_KEY`.
4. Create the PostgreSQL database named in `DATABASE_URL`.
5. Run migrations: `alembic upgrade head`
6. Start the API: `uvicorn main:app --reload`

The API documentation is available at `http://localhost:8000/docs`.

## Running an existing checkout

If the project and its `.env` file already exist, start PostgreSQL, then run:

```bash
source .venv/bin/activate
alembic upgrade head
uvicorn main:app --reload
```

The migration command creates the required tables in the database configured by `DATABASE_URL`. If that database has not been created yet, create it first (the default name is `practice_db`):

```bash
createdb practice_db
```

Open the API docs at `http://127.0.0.1:8000/docs`.

## Authentication endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/signup` | Create an account |
| `POST` | `/api/v1/auth/login` | Receive a bearer access token |
| `GET` | `/api/v1/auth/me` | Return the authenticated user |
| `POST` | `/api/v1/profile` | Create the authenticated user's profile |
| `PATCH` | `/api/v1/profile` | Update the authenticated user's profile |
| `DELETE` | `/api/v1/profile` | Permanently delete the authenticated user's profile |
| `POST` | `/api/v1/files` | Upload a file to S3 |
| `GET` | `/api/v1/files/download-url` | Create a temporary browser-ready S3 download URL |
| `GET` | `/api/v1/files/{object_key}` | Stream an uploaded file from S3 |
| `DELETE` | `/api/v1/files/{object_key}` | Delete an uploaded file from S3 |
| `POST` | `/api/v1/documents` | Upload a document and create its processing record |
| `GET` | `/api/v1/documents/{id}` | Return document processing status and analysis results |

Signup body:

```json
{"email": "user@example.com", "password": "a-secure-password"}
```

Login uses the same body and responds with `access_token` and `token_type`.
Pass that token to protected routes as `Authorization: Bearer <access_token>`.

Profile creation requires a bearer token. Example body:

```json
{
  "first_name": "Asha",
  "last_name": "Sharma",
  "date_of_birth": "1995-07-12",
  "district": "Pune",
  "state": "Maharashtra",
  "occupation": "private_sector",
  "salary_range": "50k_to_100k"
}
```

Allowed `occupation` values are `private_sector`, `government`, `unemployed`, `farmer`, `student`, and `other`. Allowed `salary_range` values are `below_10k`, `10k_to_25k`, `25k_to_50k`, `50k_to_100k`, and `above_100k`.

## File storage

Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, and `S3_BUCKET_NAME` in `.env`. File endpoints require a bearer token. Upload with a `multipart/form-data` field named `file`; the response contains an `object_key` used for reads and deletes. Use `GET /api/v1/files/download-url?object_key=...` with a bearer token to obtain a URL valid for 5 minutes by default (set `expires_in` from 1 to 3600 seconds). Each file is stored under the authenticated user's `users/{user_id}/` prefix and cannot be accessed by another user through these endpoints.

## Documents

`POST /api/v1/documents` accepts a `multipart/form-data` field named `file`, uploads it to S3, and creates a row with status `uploaded`. The row stores the immutable S3 key plus fields for future OCR (`extracted_text`) and AI output (`analysis_result`). `GET /api/v1/documents/{id}` is the client-facing polling endpoint; a future worker updates its status and results without exposing S3 credentials or object keys.
