#testing film, getfilms, recommendations
import pytest
from app.main import app
from app.core.jwt import get_current_filmuser
from starlette.responses import FileResponse
from app.models.user_models import  Profile, WatchHistory
from unittest.mock import patch, MagicMock
from pathlib import Path
import os
import tempfile

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

def test_film_streaming(client,test_film):

    test_path = Path(f"/test/path/films/{test_film.file_name}")

    # Mock only the methods that would access the file system
    with patch("builtins.open") as mock_open, \
            patch.object(Path, "stat") as mock_stat, \
            patch.object(Path, "resolve", return_value=test_path):
        
        # Configure file mock
        mock_file = MagicMock()
        mock_file.read.return_value = b"x" * 100
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Configure stat to return file size
        mock_stat.return_value = MagicMock(st_size=1000)
        
        # Test with range header
        response = client.get(
            f"/film/{test_film.file_name}",
            headers={"Range": "bytes=0-99"}
        )
        
        # Check status
        assert response.status_code == 206

def test_image(client, test_film):
   # Create a real temporary file that will exist for FileResponse
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(b"fake image content")
        temp_file.flush()
        temp_path = temp_file.name
        
        # Get the image name from the test film
        image_name = test_film.image_name
        
        # Key patch: Replace FileResponse with our controlled version
        from starlette.responses import FileResponse
        
        class MockFileResponse(FileResponse):
            def __init__(self, path, **kwargs):
                # Use our temp file instead of the requested path
                super().__init__(temp_path, **kwargs)
        
        # Apply the patches
        with patch("fastapi.responses.FileResponse", MockFileResponse), \
                patch("app.main.FileResponse", MockFileResponse), \
                patch("app.main.settings.images_dir", Path("/mocked/images/dir")), \
                patch("pathlib.Path.exists", return_value=True), \
                patch("pathlib.Path.resolve", return_value=Path(temp_path)):
            
            # Test the endpoint
            response = client.get(f"/images/{image_name}") 
    assert response.status_code == 200





def test_invalid_image(client):
    response = client.get("/images/nonexistent.jpg")

        # Verify response
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image request"