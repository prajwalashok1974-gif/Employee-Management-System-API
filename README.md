# Employee Management System API

A RESTful Employee Management API built with Python, FastAPI, PostgreSQL, and SQLAlchemy.

## Technologies

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT authentication
- Alembic
- Pytest
- Docker

## Features

- Employee CRUD operations
- User registration and login
- JWT authentication
- Role-based access control
- Password hashing
- Employee search and department filtering
- Pagination and employee statistics
- Database migrations
- Automated API tests
- Docker support
- Swagger API documentation

## Installation

Install dependencies:

```text
pip install -r requirements.txt
```

Configure `DATABASE_URL` and `SECRET_KEY` in `.env`.

Run migrations:

```text
alembic upgrade head
```

Start the server:

```text
python -m uvicorn app.main:app --reload
```

## API Documentation

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Testing

```text
pytest -v
```

## License

MIT
