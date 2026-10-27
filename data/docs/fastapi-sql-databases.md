---
title: FastAPI with SQL Databases
source: https://fastapi.tiangolo.com/tutorial/sql-databases/
---

# SQL Databases in FastAPI

FastAPI works seamlessly with any relational database and Object Relational Mapping (ORM) library in Python, such as **SQLAlchemy**, **Peewee**, **Tortoise ORM**, or **SQLModel**.

The standard recommendation in FastAPI documentation is using **SQLAlchemy** with PostgreSQL, SQLite, or MySQL.

## SQLAlchemy Setup and Configuration

When setting up SQLAlchemy with FastAPI, you typically configure three foundational components:
1. **Engine**: The database engine that manages the connection pool and dialect.
2. **SessionLocal**: A factory class that creates individual database sessions.
3. **Base**: The declarative base class that all ORM database models inherit from.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## Separating SQLAlchemy Models from Pydantic Schemas

A core design principle in FastAPI applications is keeping SQLAlchemy models separate from Pydantic schemas:
* **SQLAlchemy Models** (`models.py`): Define the actual database table structures, column types, primary keys, foreign keys, and relationships.
* **Pydantic Schemas** (`schemas.py`): Define the shapes of request bodies and response payloads, handling input validation, serialization, and OpenAPI documentation.

To enable Pydantic models to read data directly from SQLAlchemy ORM objects, set `model_config = ConfigDict(from_attributes=True)` (or `orm_mode = True` in Pydantic v1).

## Database Session Dependency with Yield

The recommended pattern for database management in FastAPI is injecting the session via a dependency using `yield`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

This guarantees:
1. A fresh database session is created for each incoming request.
2. The session is passed directly to the path operation via `db: Annotated[Session, Depends(get_db)]`.
3. The session is reliably closed after the response is sent, returning the connection to the connection pool even if an error occurs.

## CRUD Operations and Architecture

FastAPI documentation advocates separating database queries into dedicated CRUD utility functions (`crud.py`).

Path operations remain focused on HTTP concerns:
```python
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)
```

## Database Migrations with Alembic

For production database schema evolution, FastAPI projects use **Alembic**, the official migration tool for SQLAlchemy. Alembic tracks schema changes over time, generates versioned migration scripts, and applies forward and backward migrations safely.
