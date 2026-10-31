# Employee Management System API

A RESTful employee management backend built with **Python, FastAPI, PostgreSQL, and SQLAlchemy**. The project demonstrates authenticated API design, role-based access control, relational modeling, validation, migrations, and automated testing.

## Capabilities

- User registration and login with JWT access tokens
- Password hashing with `pwdlib`
- Role-based access for `admin`, `hr`, and `employee`
- Admin/HR employee create, read, update, partial update, and delete workflows
- Employee self-service profile endpoint
- Link a registered employee account to an employee record
- Search, department/status filtering, pagination, and employee statistics
- Pydantic request/response validation
- PostgreSQL persistence through SQLAlchemy
- Alembic database migrations
- Docker and Docker Compose support
- Interactive OpenAPI documentation

## Authorization model

| Role | Permissions |
| --- | --- |
| `admin` | Manage employee records, view statistics, link employee accounts |
| `hr` | Manage employee records, view statistics, link employee accounts |
| `employee` | View only their own linked employee record and their account profile |

All employee-management routes require authentication. Management operations require the `admin` or `hr` role. Public registration always creates an `employee` account; clients cannot choose or self-assign privileged roles.

### Important endpoints

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Public | Register an employee account |
| `POST` | `/auth/login` | Public | Obtain a JWT; submit email in OAuth2's `username` form field |
| `GET` | `/auth/me` | Authenticated | Get the current account |
| `GET` | `/employees/me` | Employee | Get the employee record linked to the current account |
| `POST` | `/employees/` | Admin/HR | Create an employee |
| `GET` | `/employees/` | Admin/HR | Search, filter, and paginate employees |
| `GET` | `/employees/{employee_id}` | Admin/HR | Get an employee |
| `PUT` / `PATCH` | `/employees/{employee_id}` | Admin/HR | Update an employee |
| `DELETE` | `/employees/{employee_id}` | Admin/HR | Delete an employee |
| `GET` | `/employees/stats/summary` | Admin/HR | View workforce statistics |
| `POST` | `/employees/{employee_id}/link-account` | Admin/HR | Link an existing employee account by user ID |

Send the token in the `Authorization: Bearer <token>` header for protected endpoints.

### Provision the first administrator

Privileged roles are intentionally not available through public registration. After registering the initial account, promote it through a trusted database administrator connection:

```sql
UPDATE users
SET role = 'admin'
WHERE email = 'admin@example.com';
```

To provision HR access, use the same controlled process with `role = 'hr'`. Never expose a public endpoint that lets a caller change their own role.

To connect a registered employee account to an employee record, an admin/HR user calls `POST /employees/{employee_id}/link-account` with:

```json
{
  "user_id": 12
}
```

The employee can then retrieve only their linked record through `GET /employees/me`.

## Data model

- `users`: identity, email, password hash, role, boolean active state, optional employee link, and creation time
- `employees`: contact details, job role, department, salary, employment type, status, and hire dates

The Alembic migration chain creates the users table first, then creates the employees table, converts `users.is_active` from text to boolean, and adds the optional one-to-one user/employee link.

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

Open `http://127.0.0.1:8000/docs` for Swagger UI.

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
├── routes/auth.py         # authentication and role dependencies
├── routes/employees.py    # employee endpoints and access control
├── database.py            # SQLAlchemy engine and session setup
├── models.py              # User and Employee models
└── schemas.py             # Pydantic request/response schemas
migrations/                # Alembic configuration and revisions
tests/                     # API tests
```

## Configuration safety

Never commit `.env` files, database credentials, or signing keys. Use separate development and production secrets.
