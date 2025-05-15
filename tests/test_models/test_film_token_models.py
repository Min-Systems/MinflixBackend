import pytest
from app.models.film_token_models import FilmToken
from app.models.film_models import Film

def test_film_token_model():
    """Test creating a FilmToken model."""
    film_token = FilmToken(
        id=1,
        title="Test Film",
        image_name="test.jpg",
        file_name="test.mp4"
    )
    
    assert film_token.id == 1
    assert film_token.title == "Test Film"
    assert film_token.image_name == "test.jpg"
    assert film_token.file_name == "test.mp4"
