import pytest
from fastapi.testclient import TestClient

# Import models so SQLAlchemy knows about all tables
import app.models.models  # noqa: F401

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(autouse=True)
def _setup_db():
    from app.core.database import Base
    from sqlalchemy import create_engine

    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    from app.core.database import get_db
    from app.main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient, db_session):
    from app.core.security import hash_password
    from app.models.models import User

    user = User(email="test@example.com", hashed_password=hash_password("testpass123"), full_name="Test User", role="owner")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    resp = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "testpass123"})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
