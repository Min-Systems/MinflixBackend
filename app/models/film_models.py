from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

class Film(SQLModel, table=True):
    """
        Data model for the films

        Attributes:
            id (Optional[int]): the film id
            title (str): title of the film
            length (int): length of the film
            image_name (str): the name of the film image
            file_name (str): the name of the film video
            producer (str): the producer of the film
            name (Optional[str]): name for backwards compatibility
            film_cast (List["FilmCast"]): relationship to film cast table
            production_team (List["FilmProductionTeam"]): relationship to production team
    """
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
    """
        Data model for the film cast or actors

        Attributes:
            id (Optional[int]): the id of the film cast member
            name (str): the name of the cast member
            role (str): the role of the cast member
            film_id (int): foreign key to film
            film (Film): relationship to film table
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    film_id: int = Field(foreign_key="film.id")

    # Relationship
    film: Film = Relationship(back_populates="film_cast")


class FilmProductionTeam(SQLModel, table=True):
    """
        The table for the film production team

        Attributes:
            id (Optional[int]):
            name (str):
            role (str):
            film_id (int):
            film (Film):
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    film_id: int = Field(foreign_key="film.id")

    # Relationship
    film: Film = Relationship(back_populates="production_team")