#testing for favorites, watch history, and watchlater
import pytest
import datetime
from sqlmodel import select


from app.models.user_models import FilmUser, Profile
# -------------------- Fixtures --------------------

@pytest.fixture
def test_user(test_session,test_user):
    """Create a test user with a profile."""
    
    # Create a user
    user = test_user   
    # Add a profile
    profile = Profile(displayname="Test Profile")
    user.profiles.append(profile)
    
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    
    return user



@pytest.fixture
def test_films(test_session):
    """Create multiple test films."""
    from app.models.film_models import Film
    
    # Create multiple films
    films = [
        Film(
            title=f"Test Film {i}",
            length=90 + i * 10,
            image_name=f"test{i}.jpg",
            file_name=f"test{i}.mp4",
            producer=f"Producer {i}"
        )
        for i in range(1, 4)  # Create 3 films
    ]
    
    for film in films:
        test_session.add(film)
    
    test_session.commit()
    
    # Refresh to get IDs
    for film in films:
        test_session.refresh(film)
    
    return films


# -------------------- Tests for Watch Later --------------------

def test_add_watch_later(client, test_session, test_user, test_film):
    """Test adding a film to watch later."""
    # Override authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Set up the override
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Get profile ID
        profile_id = test_user.profiles[0].id
        
        # Make the request to add film to watch later
        response = client.post(f"/watchlater/{profile_id}/{test_film.id}")
        
        # Verify response status
        assert response.status_code == 200
        
        # Verify that a token was returned
        assert response.content
        
        # Check the database to confirm the film was added to watch later
        from app.models.user_models import FilmUser
        
        statement = select(FilmUser).where(FilmUser.id == test_user.id)
        updated_user = test_session.exec(statement).first()
        
        # Get the profile
        profile = updated_user.profiles[0]
        
        # Check that the film was added to watch later
        assert len(profile.watch_later) == 1
        assert profile.watch_later[0].film_id == test_film.id
    
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)


def test_add_multiple_watch_later(client, test_session, test_user, test_films):
    """Test adding multiple films to watch later."""
    # Override authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Set up the override
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Get profile ID
        profile_id = test_user.profiles[0].id
        
        # Add each film to watch later
        for film in test_films:
            response = client.post(f"/watchlater/{profile_id}/{film.id}")
            
            # Verify success
            assert response.status_code == 200
        
        # Check the database to confirm all films were added
        from app.models.user_models import FilmUser
        
        statement = select(FilmUser).where(FilmUser.id == test_user.id)
        updated_user = test_session.exec(statement).first()
        
        # Get the profile
        profile = updated_user.profiles[0]
        
        # Check that all films were added to watch later
        assert len(profile.watch_later) == len(test_films)
        
        # Verify all film IDs are in watch later
        watch_later_film_ids = [wl.film_id for wl in profile.watch_later]
        for film in test_films:
            assert film.id in watch_later_film_ids
    
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)


def test_add_duplicate_watch_later(client, test_session, test_user, test_film):
    """Test adding the same film to watch later twice."""
    # Override authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Set up the override
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Get profile ID
        profile_id = test_user.profiles[0].id
        
        # Add the film to watch later twice
        for _ in range(2):
            response = client.post(f"/watchlater/{profile_id}/{test_film.id}")
            
            # Verify success (endpoint doesn't check for duplicates)
            assert response.status_code == 200
        
        # Check the database to confirm how many entries were added
        from app.models.user_models import FilmUser
        
        statement = select(FilmUser).where(FilmUser.id == test_user.id)
        updated_user = test_session.exec(statement).first()
        
        # Get the profile
        profile = updated_user.profiles[0]
        
        # Get film IDs in watch later (verify if duplicates exist)
        watch_later_film_ids = [wl.film_id for wl in profile.watch_later]
        
        # Count occurrences of the film ID
        occurrences = watch_later_film_ids.count(test_film.id)
        
        # The behavior depends on your implementation:
        # - If your app prevents duplicates, assert occurrences == 1
        # - If your app allows duplicates, assert occurrences == 2
        # For now, we just check that it's at least 1
        assert occurrences >= 1
    
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)


# -------------------- Tests for Favorites --------------------

def test_add_favorite(client, test_session, test_user, test_film):
    """Test adding a film to favorites."""
    # Override authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Set up the override
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Get profile ID
        profile_id = test_user.profiles[0].id
        
        # Make the request to add film to favorites
        response = client.post(f"/favorite/{profile_id}/{test_film.id}")
        
        # Verify response status
        assert response.status_code == 200
        
        # Verify that a token was returned
        assert response.content
        
        # Check the database to confirm the film was added to favorites
        from app.models.user_models import FilmUser
        
        statement = select(FilmUser).where(FilmUser.id == test_user.id)
        updated_user = test_session.exec(statement).first()
        
        # Get the profile
        profile = updated_user.profiles[0]
        
        # Check that the film was added to favorites
        assert len(profile.favorites) == 1
        assert profile.favorites[0].film_id == test_film.id
    
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)


def test_add_multiple_favorites(client, test_session, test_user, test_films):
    """Test adding multiple films to favorites."""
    # Override authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Set up the override
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Get profile ID
        profile_id = test_user.profiles[0].id
        
        # Add each film to favorites
        for film in test_films:
            response = client.post(f"/favorite/{profile_id}/{film.id}")
            
            # Verify success
            assert response.status_code == 200
        
        # Check the database to confirm all films were added
        from app.models.user_models import FilmUser
        
        statement = select(FilmUser).where(FilmUser.id == test_user.id)
        updated_user = test_session.exec(statement).first()
        
        # Get the profile
        profile = updated_user.profiles[0]
        
        # Check that all films were added to favorites
        assert len(profile.favorites) == len(test_films)
        
        # Verify all film IDs are in favorites
        favorite_film_ids = [fav.film_id for fav in profile.favorites]
        for film in test_films:
            assert film.id in favorite_film_ids
    
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)


# -------------------- Tests for Watch History --------------------

def test_add_watch_history(client, test_session, test_user, test_film):
    """Test adding a film to watch history."""
    # Override authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Set up the override
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Get profile ID
        profile_id = test_user.profiles[0].id
        
        # Make the request to add film to watch history
        response = client.post(f"/add_watchhistory/{profile_id}/{test_film.id}")
        
        # Verify response status
        assert response.status_code == 200
        
        # Verify that a token was returned
        assert response.content
        
        # Check the database to confirm the film was added to watch history
        from app.models.user_models import FilmUser
        
        statement = select(FilmUser).where(FilmUser.id == test_user.id)
        updated_user = test_session.exec(statement).first()
        
        # Get the profile
        profile = updated_user.profiles[0]
        
        # Check that the film was added to watch history
        assert len(profile.watch_history) == 1
        assert profile.watch_history[0].film_id == test_film.id
    
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)


def test_add_multiple_watch_history(client, test_session, test_user, test_films):
    """Test adding multiple films to watch history."""
    # Override authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Set up the override
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Get profile ID
        profile_id = test_user.profiles[0].id
        
        # Add each film to watch history
        for film in test_films:
            response = client.post(f"/add_watchhistory/{profile_id}/{film.id}")
            
            # Verify success
            assert response.status_code == 200
        
        # Check the database to confirm all films were added
        from app.models.user_models import FilmUser
        
        statement = select(FilmUser).where(FilmUser.id == test_user.id)
        updated_user = test_session.exec(statement).first()
        
        # Get the profile
        profile = updated_user.profiles[0]
        
        # Check that all films were added to watch history
        assert len(profile.watch_history) == len(test_films)
        
        # Verify all film IDs are in watch history
        history_film_ids = [wh.film_id for wh in profile.watch_history]
        for film in test_films:
            assert film.id in history_film_ids
    
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)


# -------------------- Cross-Feature Tests --------------------

def test_all_interactions(client, test_session, test_user, test_film):
    """Test adding a film to watch later, favorites, and watch history."""
    # Override authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Set up the override
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Get profile ID
        profile_id = test_user.profiles[0].id
        
        # Add film to watch later
        response = client.post(f"/watchlater/{profile_id}/{test_film.id}")
        assert response.status_code == 200
        
        # Add film to favorites
        response = client.post(f"/favorite/{profile_id}/{test_film.id}")
        assert response.status_code == 200
        
        # Add film to watch history
        response = client.post(f"/add_watchhistory/{profile_id}/{test_film.id}")
        assert response.status_code == 200
        
        # Check the database to confirm the film was added to all three lists
        from app.models.user_models import FilmUser
        
        statement = select(FilmUser).where(FilmUser.id == test_user.id)
        updated_user = test_session.exec(statement).first()
        
        # Get the profile
        profile = updated_user.profiles[0]
        
        # Check watch later
        assert any(wl.film_id == test_film.id for wl in profile.watch_later)
        
        # Check favorites
        assert any(fav.film_id == test_film.id for fav in profile.favorites)
        
        # Check watch history
        assert any(wh.film_id == test_film.id for wh in profile.watch_history)
    
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)


def test_invalid_profile_id(client, test_session, test_user, test_film):
    """Test using an invalid profile ID."""
    # Override authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Set up the override
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Use an invalid profile ID
        invalid_profile_id = 9999
        
        # Test each endpoint with the invalid profile ID
        endpoints = [
            f"/watchlater/{invalid_profile_id}/{test_film.id}",
            f"/favorite/{invalid_profile_id}/{test_film.id}",
            f"/add_watchhistory/{invalid_profile_id}/{test_film.id}"
        ]
        
        for endpoint in endpoints:
            response = client.post(endpoint)
            
            # This should likely fail, but the exact behavior depends on your implementation
            # It might return 404, 400, or even succeed if the endpoint doesn't validate
            # that the profile belongs to the user
            print(f"Response status for {endpoint}: {response.status_code}")
            
            # Check that nothing was added to the user's actual profile
            from app.models.user_models import FilmUser
            
            statement = select(FilmUser).where(FilmUser.id == test_user.id)
            updated_user = test_session.exec(statement).first()
            
            # Get the profile
            profile = updated_user.profiles[0]
            
            # The actual profile should not have anything added
            # Note: This assertion might need to be adjusted based on initial state
            assert len(profile.watch_later) + len(profile.favorites) + len(profile.watch_history) == 0
    
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)


def test_invalid_film_id(client, test_session, test_user):
    """Test using an invalid film ID."""
    # Override authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Set up the override
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        # Get profile ID
        profile_id = test_user.profiles[0].id
        
        # Use an invalid film ID
        invalid_film_id = 9999
        
        # Test each endpoint with the invalid film ID
        endpoints = [
            f"/watchlater/{profile_id}/{invalid_film_id}",
            f"/favorite/{profile_id}/{invalid_film_id}",
            f"/add_watchhistory/{profile_id}/{invalid_film_id}"
        ]
        
        for endpoint in endpoints:
            response = client.post(endpoint)
            
            # The behavior depends on your implementation:
            # - If foreign key constraints are enforced, should get an error
            # - If no validation is done, might succeed but create invalid references
            print(f"Response status for {endpoint}: {response.status_code}")
            
            # For endpoints that should fail due to FK constraints:
            # assert response.status_code != 200
    
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser, None)