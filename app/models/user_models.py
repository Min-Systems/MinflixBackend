from sqlmodel import Field, SQLModel, Relationship, Column
from typing import List, Optional
from pydantic import BaseModel
# from film_models import *
from .film_models import *
import datetime
from sqlalchemy import String

class FilmUser(SQLModel, table=True):
    """
    The table for the users of the application

    Attributes:
        id (Optional[int]): the id of the film user
        username (str): the username of the user which is also the email
        password (str): the password of the user
        date_registered (datetime.datetime): the date the user was registered
        profiles (List["Profile"]): sqlmodel configuration for sub-table
    """
    # Define the table name explicitly
    __tablename__ = "filmuser"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Use SQLAlchemy Column for explicit naming
    # If your database column is actually named differently, specify it here
    # Common possibilities might be 'user_name', 'email', etc.
    username: str = Field(sa_column=Column("email", String, nullable=False))
    password: str
    date_registered: datetime.datetime
    profiles: List["Profile"] = Relationship(back_populates="filmuser")


class Profile(SQLModel, table=True):
    """
        The table for the profiles of the user

        Attributes:
            id (Optional[int]): the id of the profile
            filmuserid (int): the id of the user associated with this profile
            displayname (str): the display name of the profile
            filmuser (FilmUser): relationship for sqlmodel to backpopulate
            search_history (List["SearchHistory"]): subtable for search history
            favorites (List["Favorite"]): subtable for favorites
            watch_later (List["WatchLater"]): subtable for watch later
            watch_history (List["WatchHistory"]): subtable for watch history
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    filmuserid: int = Field(foreign_key="filmuser.id")
    displayname: str

    # FilmUser Relationships
    filmuser: FilmUser = Relationship(back_populates="profiles")
    # Subtable Relationships
    search_history: List["SearchHistory"] = Relationship(back_populates="profile")
    favorites: List["Favorite"] = Relationship(back_populates="profile")
    watch_later: List["WatchLater"] = Relationship(back_populates="profile")
    watch_history: List["WatchHistory"] = Relationship(back_populates="profile")


class SearchHistory(SQLModel, table=True):
    """
        This is the table for search history

        Attributes:
            id (Optional[int]): the id of the search history
            profileid (int): the id of the profile associated with this search history
            search_query (str): the search made by the user
            profile (Profile): the relationship of the profile for back propagation
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    profileid: int = Field(foreign_key="profile.id")
    search_query: str
    profile: Profile = Relationship(back_populates="search_history")


class Favorite(SQLModel, table=True):
    """
        This is the table for the favorite films

        Attribute:
            id (Optional[int]): the id of the favorite
            profileid (int): the id of the profile associated with the favorite
            film_id (int): the id of the favorited film
            profile (Profile): the relationship of the profile for back propagation
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    profileid: int = Field(foreign_key="profile.id")
    film_id: int = Field(foreign_key="film.id")
    profile: Profile = Relationship(back_populates="favorites")


class WatchLater(SQLModel, table=True):
    """
        This is the table for films to watch later

        Attributes:
            id (Optional[int]): the id of the watch later
            profileid (int): the id of the profile associated with the watch later
            film_id (int): the id of the film to watch later
            profile (Profile): the relationship of the profile for back propagation
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    profileid: int = Field(foreign_key="profile.id")
    film_id: int = Field(foreign_key="film.id")
    profile: Profile = Relationship(back_populates="watch_later")


class WatchHistory(SQLModel, table=True):
    """
        This is the table for the watch history

        Attributes:
            id (int): the id of the watch history
            profileid (int): the id of the profile associated with the watch history
            film_id (int): the id of the film in the watch history
            profile (Profile): the relationship of the profile for back propagation
    """
    id: int = Field(default=None, primary_key=True)
    profileid: int = Field(foreign_key="profile.id")
    film_id: int = Field(foreign_key="film.id")
    profile: Profile = Relationship(back_populates="watch_history")