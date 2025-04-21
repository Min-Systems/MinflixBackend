from typing import List
from pydantic import BaseModel, ConfigDict
from .user_models import *


class TokenModel(BaseModel):
    """  
        This is the token that represent the state of the user

        Attributes
            id (int): this the film user id
            profiles (List["TokenProfileDataModel"]): list of user profiles
    """  
    id: int
    profiles: List["TokenProfileDataModel"]
    model_config = ConfigDict(from_attributes=True)


class TokenProfileDataModel(BaseModel):
    """
        This is the part of the token that represents the user profile

        Attributes:
            id (int): the id of the profile
            displayname (str): the display of the profile
            watch_later (List["TokenWatchLaterDataModel"]): the list of films to watch later
            favorites (List["TokenFavoriteDataModel"]): the list of favorite films
    """
    id: int
    displayname: str
    watch_later: List["TokenWatchLaterDataModel"]
    watch_history: List["TokenWatchHistoryDataModel"]
    favorites: List["TokenFavoriteDataModel"]
    model_config = ConfigDict(from_attributes=True)


class TokenWatchLaterDataModel(BaseModel):
    """
        This is the part of the token that represents the films to watch later

        Attributes:
            id (int): the id of the watch later
            film_id (int): the id of the film to watch later
    """
    id: int
    film_id: int
    model_config = ConfigDict(from_attributes=True)


class TokenFavoriteDataModel(BaseModel):
    """
        This is the part of the token which represents the favorites

        Attributes:
            id (int): the id of the watch later
            film_id (int): the id of the favorite film
    """
    id: int
    film_id: int
    model_config = ConfigDict(from_attributes=True)


class TokenWatchHistoryDataModel(BaseModel):
    """
        This is the part of the token which represents the favorites

        Attributes:
            id (int): the id of the watch later
            film_id (int): the id of the favorite film
    """
    id: int
    film_id: int
    model_config = ConfigDict(from_attributes=True)