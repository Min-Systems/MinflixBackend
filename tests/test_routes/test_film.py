#testing film, getfilms, recommendations

from app.main import app
from app.core.jwt import get_current_filmuser
from app.models.user_models import  Profile, WatchHistory
from unittest.mock import patch, MagicMock


def test_get_films(client):
    """Test getting all films."""
    response = client.get("/getfilms")
    
    # Just check the status code
    assert response.status_code == 200
    
    # Verify we get a list of films
    films = response.json()
    assert isinstance(films, list)
    
def test_film_endpoint_authentication(client):
    """Test that protected film endpoints require authentication."""
    # Try to access recommendations without authentication
    response = client.get("/recommendations/1")
    
    # Should fail with 401 Unauthorized
    assert response.status_code == 401

def test_mock_recommendations(client, test_session,test_film,test_user):
    """Test film recommendations with mocked authentication."""
    profile = Profile(displayname="Rec Test Profile")
    test_user.profiles = [profile]
    
    # Add to watch history
    watch_history = WatchHistory(
        profileid=profile.id,
        film_id= test_film.id
    )
    profile.watch_history = [watch_history]
    test_session.add(profile)
    test_session.commit()
    
    # Mock authentication
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Test recommendations
        response = client.get(f"/recommendations/{profile.id}")
        
        # Check that the request succeeded
        assert response.status_code == 200
        recommended_films = response.json()
        assert isinstance(recommended_films, list)
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)

def test_film_streaming(client):
    """Simple test for film streaming endpoint."""
    # Setup minimal mocks
    with patch("builtins.open", MagicMock()), \
         patch("pathlib.Path.stat") as mock_stat, \
         patch("pathlib.Path", MagicMock()):
        
        # Configure mock to return file size
        mock_stat.return_value.st_size = 1000
        
        # Test with range header
        response = client.get(
            "/film/test_film.mp4",
            headers={"Range": "bytes=0-99"}
        )
        
        # Check status code
        assert response.status_code == 206  # Partial Content

@patch.multiple(
    'pathlib.Path',
    exists=MagicMock(return_value=True),
    resolve=MagicMock(return_value="/test/path/image.jpg"),
    stat=MagicMock(return_value=MagicMock(st_size=1000)),
    __new__=MagicMock(return_value=MagicMock(suffix=".jpg"))
)
@patch('builtins.open', MagicMock())
@patch('fastapi.responses.FileResponse', MagicMock(return_value=MagicMock(status_code=200)))
def test_get_image(client):
        response = client.get("/images/test.jpg")
        assert response.status_code == 200
