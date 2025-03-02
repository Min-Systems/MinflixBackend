import os
from contextlib import asynccontextmanager
from typing import Annotated, List, Optional
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from sqlalchemy.orm import selectinload
from fastapi.middleware.cors import CORSMiddleware


'''
class Film(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
'''

# The Film Table
class Film(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    length: int
    technical_location: str
    producer: str

    # Relationships
    cast: List["Cast"] = Relationship(back_populates="film")
    production_team: List["ProductionTeam"] = Relationship(back_populates="film")


# The Cast Table (Subtable of Film)
class Cast(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    film_id: int = Field(foreign_key="film.id")

    # Relationships
    film: Film = Relationship(back_populates="cast")


# The ProductionTeam Table (Subtable of Film)
class ProductionTeam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    film_id: int = Field(foreign_key="film.id")

    # Relationships
    film: Film = Relationship(back_populates="production_team")


db_postgresql = "filmpoc"
user_postgresql = "watcher"
password_postgresql = "films"
url_postgresql = f"postgresql://{user_postgresql}:{password_postgresql}@localhost/{db_postgresql}"
engine = create_engine(url_postgresql, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_example_data(session: SessionDep):
    '''
    # make the films as data representations for the db
    films = []
    for x in range(10):
        films.append(Film(name=f"film_{x+1}"))
    # use the session and commit them to the db
    for film in films:
        session.add(film)
    session.commit()
    '''
    films = [
        Film(
            title="Echoes of Tomorrow",
            length=120,
            technical_location="Vancouver",
            producer="Elena Garcia",
            cast=[
                Cast(name="Liam Walker", role="Time Traveler"),
                Cast(name="Sophia Bennett", role="Scientist"),
                Cast(name="James Porter", role="Antagonist"),
                Cast(name="Ava Collins", role="Young Genius"),
                Cast(name="Noah Reed", role="Commander"),
            ],
            production_team=[
                ProductionTeam(name="Martha Lin", role="Director"),
                ProductionTeam(name="Carlos Reyes", role="Cinematographer"),
                ProductionTeam(name="Anika Desai", role="Editor"),
                ProductionTeam(name="David Kim", role="Composer"),
                ProductionTeam(name="Emily Stone", role="Production Designer"),
            ],
        ),
        Film(
            title="Under the Crimson Sun",
            length=140,
            technical_location="Arizona",
            producer="Jackson King",
            cast=[
                Cast(name="Amelia Hart", role="Heroine"),
                Cast(name="Oscar Blake", role="Villager"),
                Cast(name="Evelyn Brooks", role="Villain"),
                Cast(name="Ethan Cooper", role="Guide"),
                Cast(name="Zara Kane", role="Healer"),
            ],
            production_team=[
                ProductionTeam(name="Ryan Turner", role="Director"),
                ProductionTeam(name="Sophia Lee", role="Sound Designer"),
                ProductionTeam(name="Jonas Patel", role="Lighting Technician"),
                ProductionTeam(name="Kylie Ross", role="Makeup Artist"),
                ProductionTeam(name="Hunter Mitchell", role="Stunt Coordinator"),
            ],
        ),
    ]

    for film in films:
        session.add(film)
    session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_db = os.environ.get("SETUPDB")
    if setup_db == "True":
        create_db_and_tables()
        with Session(engine) as session:
            create_example_data(session)
    yield


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/films", response_model=list[Film])
def read_all_films(session: SessionDep, offset: int = 0):
    '''
    films = session.exec(select(Film).offset(offset)).all()
    return films
    '''
    # Query all films and include related cast and production team
    films = session.exec(select(Film).options(
        selectinload(Film.cast),
        selectinload(Film.production_team)
    )).all()
    return films
