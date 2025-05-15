import pytest
from app.models.token_models import (
    TokenModel, TokenProfileDataModel, 
    TokenWatchLaterDataModel, TokenFavoriteDataModel,
    TokenWatchHistoryDataModel, TokenSearchHistoryDataModel
)
from app.models.user_models import *

def test_token_model_from_film_user():
    """Test creating a TokenModel from a FilmUser."""
    # Create a sample FilmUser with profiles and related data
    user = FilmUser(
        id=1,
        username="test@example.com",
        password="password",
        date_registered=datetime.datetime.now(),
        profiles=[
            Profile(
                id=1,
                displayname="Profile 1",
                watch_later=[WatchLater(id=1, film_id=1)],
                watch_history=[WatchHistory(id=1, film_id=2)],
                search_history=[SearchHistory(id=1, search_query="action")],
                favorites=[Favorite(id=1, film_id=3)]
            )
        ]
    )
    
    # Create token model from FilmUser
    token_model = TokenModel.model_validate(user)
    
    # Test the model conversion
    assert token_model.id == 1
    assert len(token_model.profiles) == 1
    assert token_model.profiles[0].id == 1
    assert token_model.profiles[0].displayname == "Profile 1"
    assert len(token_model.profiles[0].watch_later) == 1
    assert token_model.profiles[0].watch_later[0].film_id == 1
    assert len(token_model.profiles[0].watch_history) == 1
    assert token_model.profiles[0].watch_history[0].film_id == 2
    assert len(token_model.profiles[0].favorites) == 1
    assert token_model.profiles[0].favorites[0].film_id == 3
    assert len(token_model.profiles[0].search_history) == 1
    assert token_model.profiles[0].search_history[0].search_query == "action"

def test_token_profile_data_model():
    """Test creating a TokenProfileDataModel."""
    profile_data = TokenProfileDataModel(
        id=1,
        displayname="Test Profile",
        watch_later=[],
        watch_history=[],
        search_history=[],
        favorites=[]
    )
    
    assert profile_data.id == 1
    assert profile_data.displayname == "Test Profile"
    assert profile_data.watch_later == []
    assert profile_data.watch_history == []
    assert profile_data.search_history == []
    assert profile_data.favorites == []

def test_token_watch_later_data_model():
    """Test creating a TokenWatchLaterDataModel."""
    watch_later = TokenWatchLaterDataModel(
        id=1,
        film_id=2
    )
    
    assert watch_later.id == 1
    assert watch_later.film_id == 2

def test_token_favorite_data_model():
    """Test creating a TokenFavoriteDataModel."""
    favorite = TokenFavoriteDataModel(
        id=1,
        film_id=2
    )
    
    assert favorite.id == 1
    assert favorite.film_id == 2

def test_token_watch_history_data_model():
    """Test creating a TokenWatchHistoryDataModel."""
    watch_history = TokenWatchHistoryDataModel(
        id=1,
        film_id=2
    )
    
    assert watch_history.id == 1
    assert watch_history.film_id == 2

def test_token_search_history_data_model():
    """Test creating a TokenSearchHistoryDataModel."""
    search_history = TokenSearchHistoryDataModel(
        id=1,
        search_query="test query"
    )
    
    assert search_history.id == 1
    assert search_history.search_query == "test query"