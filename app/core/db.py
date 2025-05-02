from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from .config import Settings
from ..data.film_data import *
from ..data.example_data import *
from ..models.film_models import *
from ..models.film_token_models import *
from ..models.token_models import *
from ..models.user_models import *

settings = Settings()

engine = create_engine(settings.db_url, echo=False)


def get_session():
    """
        Yields a database connection instance 

        Returns:
            Session: session object of database
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def drop_all_tables():
    """
        Wipe all data and tables from the database
    """
    SQLModel.metadata.drop_all(engine)


def create_db_and_tables():
    """
        Create the database tables
    """
    SQLModel.metadata.create_all(engine)


def create_example_data(session: SessionDep):
    """
        Add example data to database
    """
    for film in EXAMPLEFILMS:
        session.add(film)
    for user in EXAMPLEUSERS:
        session.add(user)
    session.commit()


def add_films(session: SessionDep):
    """
        Add film data to database

        Parameters:
            session (SessionDep): the database session
    """
    for film in FILMS:
        session.add(film)
    session.commit()