import pytest
from unittest.mock import patch, MagicMock
import datetime
from sqlmodel import select

from app.main import app
from app.core.jwt import get_current_filmuser
from app.core.config import Settings
from app.core.jwt import create_jwt_token, get_current_filmuser
from app.models.user_models import Profile, FilmUser, SearchHistory
from app.models.film_models import Film
from app.models.token_models import TokenModel

# -------------------- Fixtures --------------------

@pytest.fixture
def test_user(test_session):
    
    # Create a user
    settings = Settings()
    user = FilmUser(
        username="searchtest@example.com",
        password=settings.pwd_context.hash("testpassword"),
        date_registered=datetime.datetime.now(),
        profiles=[]
    )
    
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    
    return user


@pytest.fixture
def test_profile(test_session, test_user):
    """Create a test profile for search tests."""
    
    # Create a profile
    profile = Profile(
        displayname="Search Test Profile",
        filmuserid=test_user.id
    )
    
    test_user.profiles.append(profile)
    test_session.add(test_user)
    test_session.commit()
    test_session.refresh(profile)
    
    return profile


@pytest.fixture
def test_films(test_session):
    """Create test films for search tests."""
    
    # Create test films with different titles
    films = [
        Film(
            title="Action Movie",
            length=120,
            image_name="action.jpg",
            file_name="action.mp4",
            producer="Action Producer"
        ),
        Film(
            title="Comedy Film",
            length=95,
            image_name="comedy.jpg",
            file_name="comedy.mp4",
            producer="Comedy Producer"
        ),
        Film(
            title="Drama Picture",
            length=150,
            image_name="drama.jpg",
            file_name="drama.mp4",
            producer="Drama Producer"
        )
    ]
    
    for film in films:
        test_session.add(film)
    
    test_session.commit()
    
    # Refresh to get IDs
    for film in films:
        test_session.refresh(film)
    
    return films


@pytest.fixture
def auth_token(test_user):
    """Create a JWT token for authentication."""
    
    # Create token data from the user
    token_data = TokenModel.model_validate(test_user).model_dump()
    
    # Create the token
    return create_jwt_token(token_data)


@pytest.fixture
def auth_headers(auth_token):
    """Create authentication headers with the token."""
    return {"Authorization": f"Bearer {auth_token}"}


# -------------------- Tests --------------------

def test_search_basic(client, test_session, test_user, test_profile, test_films, auth_headers):
    """Test basic search functionality."""
    
    # Override authentication dependency
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Perform a search for "Action" which should match the first film
        response = client.post(
            "/search",
            data={
                "profile_id": str(test_profile.id),
                "query": "Action"
            },
            headers=auth_headers
        )
        
        # Print response for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.content}")
        
        # Verify the response
        assert response.status_code == 200
        
        # Check the response structure
        data = response.json()
        assert "results" in data
        assert "token" in data
        
        # Verify that the film was found (should be the first film)
        assert test_films[0].id in data["results"]
    finally:
        # Clean up the override
        app.dependency_overrides.pop(get_current_filmuser, None)


def test_search_no_results(client, test_profile, test_user, auth_headers):
    """Test search with no matching results."""
    # Override authentication dependency
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Perform a search with a query that shouldn't match anything
        response = client.post(
            "/search",
            data={
                "profile_id": str(test_profile.id),
                "query": "NoMatchingFilmWithThisTitle"
            },
            headers=auth_headers
        )
        
        # Verify the response
        assert response.status_code == 200
        
        # Check that there are no results
        data = response.json()
        assert len(data["results"]) == 0
        assert "token" in data  # The token should still be returned
    finally:
        # Clean up the override
        app.dependency_overrides.pop(get_current_filmuser, None)


def test_search_history(client, test_session, test_profile, test_user, auth_headers):
    """Test that search queries are added to search history."""
    
    # Override authentication dependency
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Perform a search
        query = "HistoryTestQuery"
        response = client.post(
            "/search",
            data={
                "profile_id": str(test_profile.id),
                "query": query
            },
            headers=auth_headers
        )
        
        # Verify the response is successful
        assert response.status_code == 200
        
        
        statement = select(FilmUser).where(FilmUser.id == test_user.id)
        updated_user = test_session.exec(statement).first()
        
        # Get the profile
        updated_profile = updated_user.profiles[0]
        
        # Check that the search query was added to history
        search_queries = [sh.search_query for sh in updated_profile.search_history]
        assert query in search_queries
    finally:
        # Clean up the override
        app.dependency_overrides.pop(get_current_filmuser, None)


def test_search_history_limit(client, test_session, test_profile, test_user, auth_headers):
    """Test that search history is limited to 3 items."""
    
    # Add 3 initial searches
    for i in range(3):
        test_profile.search_history.append(
            SearchHistory(profileid=test_profile.id, search_query=f"OldQuery{i}")
        )
    
    test_session.add(test_profile)
    test_session.commit()
    test_session.refresh(test_profile)
    
    # Verify we have 3 search history items
    assert len(test_profile.search_history) == 3
    
    
    # Override authentication dependency
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Perform a new search
        new_query = "NewSearchQuery"
        response = client.post(
            "/search",
            data={
                "profile_id": str(test_profile.id),
                "query": new_query
            },
            headers=auth_headers
        )
        
        # Verify the response is successful
        assert response.status_code == 200
        
        
        statement = select(FilmUser).where(FilmUser.id == test_user.id)
        updated_user = test_session.exec(statement).first()
        
        # Get the profile
        updated_profile = updated_user.profiles[0]
        
        # Check that there are still only 3 search history items
        assert len(updated_profile.search_history) == 3
        
        # Check that the oldest search was removed and the new one was added
        search_queries = [sh.search_query for sh in updated_profile.search_history]
        assert new_query in search_queries
        assert "OldQuery0" not in search_queries  # The oldest should be gone
    finally:
        # Clean up the override
        app.dependency_overrides.pop(get_current_filmuser, None)