import pytest
from sqlmodel import Session, SQLModel, select
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.core.db import (
    get_session, 
    drop_all_tables, 
    create_db_and_tables, 
    create_example_data,
    add_films,
    engine
)
from app.models.film_models import Film
from app.models.user_models import FilmUser


@pytest.fixture
def mock_engine():
    """Mock SQLModel engine."""
    with patch('app.core.db.engine') as mock_engine:
        yield mock_engine


@pytest.fixture
def mock_session():
    """Create a mock session."""
    mock = MagicMock(spec=Session)
    return mock


def test_get_session():
    """Test get_session generator yields a session."""
    # Test that the generator yields a session
    session_generator = get_session()
    with patch('app.core.db.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        # Get the session from the generator
        session = next(session_generator)
        
        # Verify session was created with the engine
        mock_session_class.assert_called_once_with(engine)
        assert session == mock_session


def test_drop_all_tables(mock_engine):
    """Test drop_all_tables calls SQLModel.metadata.drop_all."""
    with patch('app.core.db.SQLModel') as mock_sqlmodel:
        drop_all_tables()
        
        # Verify the metadata drop_all method was called with the engine
        mock_sqlmodel.metadata.drop_all.assert_called_once_with(mock_engine)


def test_create_db_and_tables(mock_engine):
    """Test create_db_and_tables calls SQLModel.metadata.create_all."""
    with patch('app.core.db.SQLModel') as mock_sqlmodel:
        create_db_and_tables()
        
        # Verify the metadata create_all method was called with the engine
        mock_sqlmodel.metadata.create_all.assert_called_once_with(mock_engine)


def test_create_example_data(mock_session):
    """Test create_example_data adds example data to the session."""
    with patch('app.core.db.EXAMPLEFILMS', ['film1', 'film2']), \
         patch('app.core.db.EXAMPLEUSERS', ['user1', 'user2']):
        
        create_example_data(mock_session)
        
        # Verify each film and user was added to the session
        assert mock_session.add.call_count == 4
        mock_session.commit.assert_called_once()


def test_add_films(mock_session):
    """Test add_films adds films to the session."""
    with patch('app.core.db.FILMS', ['film1', 'film2', 'film3']):
        add_films(mock_session)
        
        # Verify each film was added to the session
        assert mock_session.add.call_count == 3
        mock_session.commit.assert_called_once()


# Integration tests with actual in-memory database
@pytest.fixture
def test_db_session():
    """Create a test database session with actual SQLite in-memory database."""
    from sqlmodel import create_engine
    
    # Create in-memory SQLite database
    test_engine = create_engine("sqlite:///:memory:")
    
    # Create all tables
    SQLModel.metadata.create_all(test_engine)
    
    with Session(test_engine) as session:
        yield session
    
    # Clean up
    SQLModel.metadata.drop_all(test_engine)


def test_create_example_data_integration(test_db_session):
    """Integration test for create_example_data with actual database."""
    # Patch example data to ensure we know what's being added
    test_film = Film(
        title="Test Film",
        length=120,
        image_name="test.jpg",
        file_name="test.mp4",
        producer="Test Producer"
    )
    
    test_user = FilmUser(
        username="test@example.com",
        password="hashed_password",
        date_registered=datetime.now()
    )
    
    with patch('app.core.db.EXAMPLEFILMS', [test_film]), \
         patch('app.core.db.EXAMPLEUSERS', [test_user]):
        
        create_example_data(test_db_session)
        
        # Query the database to verify data was added
        films = test_db_session.exec(select(Film)).all()
        users = test_db_session.exec(select(FilmUser)).all()
        
        assert len(films) == 1
        assert films[0].title == "Test Film"
        
        assert len(users) == 1
        assert users[0].username == "test@example.com"


def test_add_films_integration(test_db_session):
    """Integration test for add_films with actual database."""
    # Patch film data
    test_films = [
        Film(
            title=f"Test Film {i}",
            length=90 + i*10,
            image_name=f"test{i}.jpg",
            file_name=f"test{i}.mp4",
            producer=f"Producer {i}"
        )
        for i in range(3)
    ]
    
    with patch('app.core.db.FILMS', test_films):
        add_films(test_db_session)
        
        # Query the database to verify films were added
        films = test_db_session.exec(select(Film)).all()
        
        assert len(films) == 3
        assert {film.title for film in films} == {"Test Film 0", "Test Film 1", "Test Film 2"}