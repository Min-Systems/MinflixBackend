from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

class Film(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    length: int
    image_name: str
    file_name: str
    producer: str
    name: Optional[str] = None  # Added for backward compatibility

    # Relationships
    film_cast: List["FilmCast"] = Relationship(back_populates="film")
    production_team: List["FilmProductionTeam"] = Relationship(back_populates="film")


class FilmCast(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    film_id: int = Field(foreign_key="film.id")

    # Relationship
    film: Film = Relationship(back_populates="film_cast")


class FilmProductionTeam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    film_id: int = Field(foreign_key="film.id")

    # Relationship
    film: Film = Relationship(back_populates="production_team")
