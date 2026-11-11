import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db, sqlite_pragmas   # sqlite_pragmas 见第 6 步
from main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
event.listen(engine, "connect", sqlite_pragmas)


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def alice(client):
    client.post("/users/register", json={"username": "alice", "password": "secret123"})
    r = client.post("/users/login", data={"username": "alice", "password": "secret123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}