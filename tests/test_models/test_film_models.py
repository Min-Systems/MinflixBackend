import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from app.models.film_models import Film, FilmCast, FilmProductionTeam

def test_film_model_creation():
    """Test that a Film model can be created with valid data."""
    film = Film(
        title="Test Film",
        length=120,
        image_name="test.jpg",
        file_name="test.mp4",
        producer="Test Producer"
    )
    
    assert film.title == "Test Film"
    assert film.length == 120
    assert film.image_name == "test.jpg"
    assert film.file_name == "test.mp4"
    assert film.producer == "Test Producer"
    assert film.id is None  # ID should be None until persisted

def test_film_relationships(test_session):
    """Test Film model relationships with FilmCast and FilmProductionTeam."""
    # Create a film with cast and crew
    film = Film(
        title="Relationship Test Film",
        length=120,
        image_name="test.jpg",
        file_name="test.mp4",
        producer="Test Producer"
    )
    
    # Add cast members
    cast1 = FilmCast(name="Actor 1", role="Main Character")
    cast2 = FilmCast(name="Actor 2", role="Supporting Role")
    film.film_cast = [cast1, cast2]
    
    # Add production team members
    crew1 = FilmProductionTeam(name="Director Name", role="Director")
    crew2 = FilmProductionTeam(name="Writer Name", role="Screenwriter")
    film.production_team = [crew1, crew2]
    
    # Save to database
    test_session.add(film)
    test_session.commit()
    test_session.refresh(film)
    
    # Verify relationships were saved
    assert len(film.film_cast) == 2
    assert film.film_cast[0].name == "Actor 1"
    assert film.film_cast[1].role == "Supporting Role"
    
    assert len(film.production_team) == 2
    assert film.production_team[0].name == "Director Name"
    assert film.production_team[1].role == "Screenwriter"
    
    # Test back-references
    crew = test_session.exec(select(FilmProductionTeam).where(
        FilmProductionTeam.role == "Director")).first()
    assert crew.film.title == "Relationship Test Film"

def test_film_cast_model():
    """Test that the FilmCast model can be created with valid data."""
    film_cast = FilmCast(
        name="Test Actor",
        role="Test Role",
        film_id=1
    )
    
    assert film_cast.name == "Test Actor"
    assert film_cast.role == "Test Role"
    assert film_cast.film_id == 1
    assert film_cast.id is None

def test_film_production_team_model():
    """Test that the FilmProductionTeam model can be created with valid data."""
    production_team = FilmProductionTeam(
        name="Test Crew",
        role="Test Role",
        film_id=1
    )
    
    assert production_team.name == "Test Crew"
    assert production_team.role == "Test Role"
    assert production_team.film_id == 1
    assert production_team.id is None