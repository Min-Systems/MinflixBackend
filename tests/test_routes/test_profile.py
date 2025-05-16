from app.main import app
from app.core.jwt import get_current_filmuser
from app.models.user_models import Profile


def test_edit_auth(client, test_session):
    # Make the request to edit a non-existent profile
    response = client.post(
        "/editprofile",
        data={
            "displayname": "Non-Existent Profile",
            "newdisplayname": "New Name"
        }
    )
    
    assert response.status_code == 401
    

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

def test_edit_profile(client, test_session, test_user):
    """Test editing a profile."""
    #add profile to test user
    profile = Profile(displayname="Rec Test Profile")
    test_user.profiles = [profile]
    test_session.add(profile)
    test_session.commit()
    test_session.refresh(test_user)

    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    try:
        # Assuming the first profile is the one we want to edit
        original_name = test_user.profiles[0].displayname
        new_name = "Updated Profile Name"
        
        response = client.post(
            "/editprofile",
            data={
                "displayname": original_name,
                "newdisplayname": new_name
            }
        )
        
        # Check response
        assert response.status_code == 200
        assert response.content  # Should contain a token
        
        # Verify that the profile name was updated
        updated_profile = test_user.profiles[0]
        assert updated_profile.displayname == new_name
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser)