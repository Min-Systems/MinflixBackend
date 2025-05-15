#testing profile related routes(add, edit, watchlater, favorite, watchhistory)

from app.main import app
from app.core.jwt import get_current_filmuser

def test_add_profile(client, test_user):
    """Test adding a profile."""
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    try:
        response = client.post(
            "/addprofile",
            data={"displayname": "Test Profile"}
        )
        # Check response
        assert response.status_code == 200
        assert response.content  # Should contain a token
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser)