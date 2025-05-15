import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
import datetime

from app.main import app
from app.core.db import get_session
from app.models.user_models import FilmUser, Profile
from app.models.film_models import Film
from app.core.config import Settings

# Override the dependency to use the test database
@pytest.fixture(scope="session")
def test_engine():
    """Create a SQLite in-memory database for testing."""
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

@pytest.fixture
def test_session(test_engine):
    """Create test database session."""
    SQLModel.metadata.create_all(test_engine)
    
    with Session(test_engine) as session:
        yield session
        
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture
def client(test_session):
    """Create a test client with the test database."""
    def override_get_session():
        yield test_session
        
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_session):
    """Create a test user in the database."""
    settings = Settings()
    
    user = FilmUser(
        username="testuser@example.com",
        password=settings.pwd_context.hash("testpassword"),
        date_registered=datetime.datetime.now(),
        profiles=[]
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    
    return user

@pytest.fixture
def test_film(test_session):
    """Create a test film in the database."""
    film = Film(
        title="Test Film",
        length=120,
        image_name="test.jpg",
        file_name="test.mp4",
        producer="Test Producer"
    )
    test_session.add(film)
    test_session.commit()
    test_session.refresh(film)
    
    return film

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers with a valid JWT token."""
    response = client.post(
        "/login",
        data={"username": test_user.username, "password": "testpassword"}
    )
    token = response.content.decode()
    
    return {"Authorization": f"Bearer {token}"}
