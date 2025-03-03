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
    # Nested FilmCast data
    film_cast: List[FilmCastRead]
    # Nested Production data
    production_team: List[FilmProductionTeamRead]

    class Config:
        # Enables serialization from ORM objects
        orm_mode = True  
