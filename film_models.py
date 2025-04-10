from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

<<<<<<< HEAD
# The Film Table
=======

>>>>>>> develop
class Film(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    length: int
<<<<<<< HEAD
    technical_location: str
=======
    image_name: str
    file_name: str
>>>>>>> develop
    producer: str
    name: Optional[str] = None  # Added for backward compatibility

    # Relationships
    film_cast: List["FilmCast"] = Relationship(back_populates="film")
    production_team: List["FilmProductionTeam"] = Relationship(back_populates="film")


<<<<<<< HEAD
# The FilmCast Table (Subtable of Film)
=======
>>>>>>> develop
class FilmCast(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    film_id: int = Field(foreign_key="film.id")

    # Relationship
    film: Film = Relationship(back_populates="film_cast")


<<<<<<< HEAD
# The FilmProductionTeam Table (Subtable of Film)
=======
>>>>>>> develop
class FilmProductionTeam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    film_id: int = Field(foreign_key="film.id")

    # Relationship
    film: Film = Relationship(back_populates="production_team")
<<<<<<< HEAD


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
    name: Optional[str] = None  # Added for backward compatibility
    # Nested FilmCast data
    film_cast: List[FilmCastRead]
    # Nested Production data
    production_team: List[FilmProductionTeamRead]

    class Config:
        orm_mode = True
=======
>>>>>>> develop
