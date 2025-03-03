from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from film_models import *

class FilmUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password: str
    date_registered: str
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
    profile: Profile = Relationship(back_populates="watch_history")


class WatchHistoryRead(SQLModel):
    id: int
    profileid: int
    film_id: int
    timestamp: int
    completion: int
    datewatched: str


class WatchLaterRead(SQLModel):
    id: int
    profileid: int
    film_id: int
    dateadded: str


class FavoriteRead(SQLModel):
    id: int
    profileid: int
    film_id: int
    favorited_date: str


class SearchHistoryRead(SQLModel):
    id: int
    profileid: int
    search_query: str


class ProfileRead(SQLModel):
    id: int
    filmuserid: int
    displayname: str

    search_history: List[SearchHistoryRead]
    favorites: List[FavoriteRead]
    watch_later: List[WatchLaterRead]
    watch_history: List[WatchHistoryRead]


class FilmUserRead(SQLModel):
    id: int
    email: str
    password: str
    date_registered: str
    
    profiles: List[ProfileRead]

    class Config:
        orm_mode = True

