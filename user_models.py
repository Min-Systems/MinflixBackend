from sqlmodel import Field, SQLModel, Relationship, Column
from typing import List, Optional
from pydantic import BaseModel
from film_models import *
import datetime
from sqlalchemy import String

class FilmUser(SQLModel, table=True):
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


<<<<<<< HEAD
# The rest of your model definitions remain the same
=======
>>>>>>> develop
class SearchHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profileid: int = Field(foreign_key="profile.id")
    search_query: str
    profile: Profile = Relationship(back_populates="search_history")


class Favorite(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profileid: int = Field(foreign_key="profile.id")
    film_id: int = Field(foreign_key="film.id")
    favorited_date: str
    profile: Profile = Relationship(back_populates="favorites")


class WatchLater(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profileid: int = Field(foreign_key="profile.id")
    film_id: int = Field(foreign_key="film.id")
    dateadded: str
    profile: Profile = Relationship(back_populates="watch_later")


class WatchHistory(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    profileid: int = Field(foreign_key="profile.id")
    film_id: int = Field(foreign_key="film.id")
    timestamp: Optional[int]
    completion: Optional[int]
    datewatched: str
<<<<<<< HEAD
    profile: Profile = Relationship(back_populates="watch_history")
=======
    profile: Profile = Relationship(back_populates="watch_history")
>>>>>>> develop
