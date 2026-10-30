from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routes.employees import router as employee_router
from app.routes.auth import router as auth_router


app = FastAPI(
    title="Employee Management System API",
    description="Employee Management REST API built with FastAPI and PostgreSQL",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(employee_router)


@app.get("/", tags=["General"])
def home():

    return {
        "message": "Employee Management System API",
        "status": "running",
        "documentation": "/docs"
    }


@app.get("/health", tags=["General"])
def health_check():

    return {"status": "healthy"}


@app.get("/database-health", tags=["General"])
def database_health():

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "connected",
        "database": "employee_db"
    }