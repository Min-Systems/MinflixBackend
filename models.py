from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

# The Film Table
class Film(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    length: int
    technical_location: str
    producer: str

    # Relationships
    film_cast: List["FilmCast"] = Relationship(back_populates="film")
    production_team: List["FilmProductionTeam"] = Relationship(back_populates="film")

    class Config:
        table_args = {"extend_existing": True}


# The FilmCast Table (Subtable of Film)
class FilmCast(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    film_id: int = Field(foreign_key="film.id")

    # Relationship
    film: Film = Relationship(back_populates="film_cast")


# The FilmProductionTeam Table (Subtable of Film)
class FilmProductionTeam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    film_id: int = Field(foreign_key="film.id")

    # Relationship
    film: Film = Relationship(back_populates="production_team")


# Pydantic models for nested relationships
class FilmCastRead(SQLModel):
    id: int
    name: str
    role: str


class FilmProductionTeamRead(SQLModel):
    id: int
    name: str
    role: str


class FilmRead(SQLModel):
    id: int
    title: str
    length: int
    technical_location: str
    producer: str
    film_cast: List[FilmCastRead]  # Nested FilmCast data
    production_team: List[FilmProductionTeamRead]  # Nested ProductionTeam data

    class Config:
        orm_mode = True  # Enables serialization from ORM objects


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
