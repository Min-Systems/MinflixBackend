import pytest
import datetime
from sqlmodel import select
from app.models.user_models import (
    FilmUser, Profile, SearchHistory, 
    Favorite, WatchLater, WatchHistory
)

def test_film_user_model():
    """Test that the FilmUser model can be created with valid data."""
    user = FilmUser(
        username="test@example.com",
        password="hashed_password",
        date_registered=datetime.datetime(2023, 1, 1)
    )
    
    assert user.username == "test@example.com"
    assert user.password == "hashed_password"
    assert user.date_registered == datetime.datetime(2023, 1, 1)
    assert user.profiles == []
    assert user.id is None

def test_profile_model():
    """Test that the Profile model can be created with valid data."""
    profile = Profile(
        displayname="Test Profile",
        filmuserid=1
    )
    
    assert profile.displayname == "Test Profile"
    assert profile.filmuserid == 1
    assert profile.id is None
    assert profile.search_history == []
    assert profile.favorites == []
    assert profile.watch_later == []
    assert profile.watch_history == []

def test_user_profile_relationship(test_session):
    """Test the relationship between FilmUser and Profile."""
    user = FilmUser(
        username="relationship@test.com",
        password="password",
        date_registered=datetime.datetime.now()
    )
    
    profile1 = Profile(displayname="Profile 1")
    profile2 = Profile(displayname="Profile 2")
    
    user.profiles = [profile1, profile2]
    
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    
    # Test the relationship from user to profiles
    assert len(user.profiles) == 2
    assert user.profiles[0].displayname == "Profile 1"
    
    # Test the relationship from profile to user
    stored_profile = test_session.exec(select(Profile).where(
        Profile.displayname == "Profile 1")).first()
    assert stored_profile.filmuser.username == "relationship@test.com"

def test_profile_related_models(test_session, test_film):
    """Test the relationships between Profile and its related models."""
    # Create user and profile
    user = FilmUser(
        username="related@test.com",
        password="password",
        date_registered=datetime.datetime.now()
    )
    profile = Profile(displayname="Related Test")
    user.profiles = [profile]
    
    test_session.add(user)
    test_session.commit()
    test_session.refresh(profile)
    
    # Add search history
    search = SearchHistory(profileid=profile.id, search_query="test query")
    profile.search_history.append(search)
    
    # Add favorite
    favorite = Favorite(profileid=profile.id, film_id=test_film.id)
    profile.favorites.append(favorite)
    
    # Add watch later
    watch_later = WatchLater(profileid=profile.id, film_id=test_film.id)
    profile.watch_later.append(watch_later)
    
    # Add watch history
    watch_history = WatchHistory(profileid=profile.id, film_id=test_film.id)
    profile.watch_history.append(watch_history)
    
    test_session.add(profile)
    test_session.commit()
    test_session.refresh(profile)
    
    # Test relationships
    assert len(profile.search_history) == 1
    assert profile.search_history[0].search_query == "test query"
    
    assert len(profile.favorites) == 1
    assert profile.favorites[0].film_id == test_film.id
    
    assert len(profile.watch_later) == 1
    assert profile.watch_later[0].film_id == test_film.id
    
    assert len(profile.watch_history) == 1
    assert profile.watch_history[0].film_id == test_film.id