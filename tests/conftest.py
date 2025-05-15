import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool
import datetime
from unittest.mock import patch, MagicMock

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
        title="Evil Brain From Outer Space",  
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


@pytest.fixture
def mock_app():
    """Create a mock FastAPI app."""
    return MagicMock()


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session_mock = MagicMock()
    session_mock.exec = MagicMock()
    session_mock.exec.return_value = MagicMock()
    session_mock.exec.return_value.first = MagicMock(return_value=None)  # No films by default
    return session_mock


@pytest.fixture
def mock_db_dependencies(mock_db_session):
    """Create mock patches for database dependencies."""
    # Create all the patches
    patches = {
        'Session': patch('app.main.Session'),
        'drop_all_tables': patch('app.main.drop_all_tables'),
        'create_db_and_tables': patch('app.main.create_db_and_tables'),
        'create_example_data': patch('app.main.create_example_data'),
        'select': patch('app.main.select'),
        'add_films': patch('app.main.add_films'),
        'settings': patch('app.main.settings')
    }
    
    # Start all patches
    mocks = {name: p.start() for name, p in patches.items()}
    
    # Configure the session mock
    mocks['Session'].return_value.__enter__.return_value = mock_db_session
    
    # Yield the mocks and patches for cleanup
    yield mocks
    
    # Stop all patches
    for p in patches.values():
        p.stop()


@pytest.fixture
def dynamic_mode_config(mock_db_dependencies):
    """Configure settings for Dynamic mode."""
    mock_db_dependencies['settings'].db_setup = "Dynamic"
    return mock_db_dependencies


@pytest.fixture
def production_mode_config(mock_db_dependencies):
    """Configure settings for Production mode."""
    mock_db_dependencies['settings'].db_setup = "Production"
    return mock_db_dependencies


@pytest.fixture
def example_mode_config(mock_db_dependencies):
    """Configure settings for Example mode."""
    mock_db_dependencies['settings'].db_setup = "Example"
    return mock_db_dependencies


@pytest.fixture
def films_present_config(mock_db_dependencies, mock_db_session):
    """Configure database to have films present."""
    mock_db_session.exec.return_value.first.return_value = MagicMock()  # Films present
    return mock_db_dependencies

