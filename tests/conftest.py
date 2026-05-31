"""Shared pytest fixtures.

Spins up an isolated in-memory SQLite database per test and overrides the
app's ``get_db`` dependency so requests hit the test database instead of the
real one. Nothing here touches PostgreSQL or any production data.
"""

import os

# Must be set before importing the app, since app.database reads it at import
# time and main.py builds the JWT layer from it.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from main import app

# A single shared in-memory database for the test. StaticPool keeps one
# connection alive so every session sees the same tables and rows.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    """Create all tables, yield a session, then drop everything for isolation."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """A TestClient whose get_db dependency is bound to the test session."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    """Register a normal (non-admin) user and return bearer auth headers."""
    response = client.post(
        "/api/users/register",
        json={
            "username": "citizen",
            "password": "secret123",
            "fullName": "Test Citizen",
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
