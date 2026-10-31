# Employee Management System API

A RESTful employee management backend built with **Python, FastAPI, PostgreSQL, and SQLAlchemy**. The project demonstrates authenticated API design, relational modeling, validation, migrations, and automated testing.

## Capabilities

- User registration and login
- JWT access-token authentication
- Password hashing with `pwdlib`
- Employee create, read, update, partial update, and delete workflows
- Search, department filtering, pagination, and employee statistics
- Pydantic request/response validation
- PostgreSQL persistence through SQLAlchemy
- Alembic database migrations
- Docker and Docker Compose support
- Interactive OpenAPI documentation

## API surface

### General

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Service status and documentation link |
| `GET` | `/health` | Application health check |
| `GET` | `/database-health` | Database connectivity check |

### Authentication

The auth router provides registration and login endpoints. Login returns a JWT that authenticated employee routes can use through the `Authorization: Bearer <token>` header. See the generated `/docs` page for the exact request and response schemas.

### Employees

The employee router provides CRUD operations, partial updates, search/filtering, pagination, and statistics. Request models validate email addresses, required text lengths, salary bounds, and optional employee fields before database access.

## Data model

The core relational model contains:

- `users`: identity, email, password hash, role, active state, and creation time
- `employees`: contact details, role, department, salary, employment type, status, and hire dates

Alembic migrations in [`migrations/versions`](migrations/versions) provide reproducible schema changes.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with a PostgreSQL `DATABASE_URL` and a strong `SECRET_KEY`, then run:

```bash
alembic upgrade head
python -m uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger UI.

## Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest -v
```

## Project structure

```text
app/
├── core/security.py       # password hashing and JWT helpers
├── routes/auth.py         # authentication endpoints
├── routes/employees.py    # employee endpoints
├── database.py            # SQLAlchemy engine and session setup
├── models.py              # User and Employee models
└── schemas.py             # Pydantic request/response schemas
migrations/                # Alembic configuration and revisions
tests/                     # API tests
```

## Configuration safety

Never commit `.env` files, database credentials, or signing keys. Use separate development and production secrets.