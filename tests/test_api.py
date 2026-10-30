import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_database_health():
    response = client.get("/database-health")

    assert response.status_code == 200
    assert response.json()["status"] == "connected"


def test_employee_endpoint_requires_authentication():
    response = client.get("/employees/")

    assert response.status_code == 401


def test_user_registration():
    unique_email = f"{uuid.uuid4().hex}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": unique_email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == unique_email