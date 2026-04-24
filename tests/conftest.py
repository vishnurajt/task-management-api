import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use separate SQLite database for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the real database with test database
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    # Create all tables before each test
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after each test — clean slate
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "test1234"
    })
    return response.json()


@pytest.fixture
def auth_headers(client):
    # Register and login, return auth headers
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "test1234"
    })
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "test1234"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}