import os
from contextlib import asynccontextmanager
from typing import Annotated, List
from fastapi import Depends, FastAPI 
from sqlmodel import Session, SQLModel, create_engine, select, Relationship
from sqlalchemy.orm import selectinload
from fastapi.middleware.cors import CORSMiddleware
from models import *
from film_models import *
from example_data import *


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
    for film in EXAMPLEFILMS:
        session.add(film)
    for user in EXAMPLEUSERS:
        session.add(user)
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


@app.get("/films", response_model=List[FilmRead])
def read_all_films(session: SessionDep):
    statement = select(Film).options(
        selectinload(Film.film_cast),
        selectinload(Film.production_team)
    )
    films = session.exec(statement).all()
    return films


@app.get("/users")
def read_all_users(session: SessionDep, response_model=List[FilmUserRead]):
    statement = select(FilmUser).options(
        selectinload(FilmUser.profiles).selectinload(Profile.search_history),
        selectinload(FilmUser.profiles).selectinload(Profile.favorites),
        selectinload(FilmUser.profiles).selectinload(Profile.watch_later),
        selectinload(FilmUser.profiles).selectinload(Profile.watch_history),
    )
    users = session.exec(statement).all()
    return users