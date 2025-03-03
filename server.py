import os
from contextlib import asynccontextmanager
from typing import Annotated, List
from fastapi import Depends, FastAPI, Response
from sqlmodel import Session, SQLModel, create_engine, select, Relationship
from sqlalchemy.orm import selectinload
from fastapi.middleware.cors import CORSMiddleware
from film_models import *
from user_models import *
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
    #for film in EXAMPLEFILMS:
    #    session.add(film)
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
def read_all_users(session: SessionDep):
    '''
    statement = select(FilmUser).options(
        selectinload(FilmUser.profiles).selectinload(Profile.search_history),
        selectinload(FilmUser.profiles).selectinload(Profile.favorites),
        selectinload(FilmUser.profiles).selectinload(Profile.watch_later),
        selectinload(FilmUser.profiles).selectinload(Profile.watch_history),
    )
    users = session.exec(statement).all()
    return users
    '''
    statement = select(FilmUser)
    users = session.exec(statement).all()

    data = ""
    for user in users:
        data += f"id: {user.id}, email: {user.email}, password: {user.password} + date_registered: {user.date_registered}\n"
        for profile in user.profiles:
            data += f"displayname: {profile.displayname}\n"
            for search in profile.search_history:
                data += f"search_query: {search.search_query}\n"
            for favorite in profile.favorites:
                data += f"favorite: {favorite.favorited_date} film_id: {favorite.film_id}\n"
            for watchlater in profile.watch_later:
                data += f"dateadded: {watchlater.dateadded} film_id: {watchlater.film_id}\n"
            for watchhistory in profile.watch_history:
                data += f"datewatched: {watchhistory.datewatched} film_id: {watchlater.film_id}\n"

    return Response(content=data)