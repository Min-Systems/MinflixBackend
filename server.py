import os
import jwt
import datetime
from contextlib import asynccontextmanager
from typing import Annotated, List
from fastapi import Depends, FastAPI, Response, Form, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.orm import selectinload
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from film_models import *
from user_models import *
from example_data import *
from token_models import *


db_postgresql = "filmpoc"
user_postgresql = "watcher"
password_postgresql = "films"
url_postgresql = f"postgresql://{user_postgresql}:{password_postgresql}@localhost/{db_postgresql}"
engine = create_engine(url_postgresql, echo=True)


# openssl rand -hex 32 to generate key(more on this later)
SECRET_KEY = "abc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def drop_all_tables():
    SQLModel.metadata.drop_all(engine)


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
    if setup_db == "Example":
        drop_all_tables()
        create_db_and_tables()
        with Session(engine) as session:
            create_example_data(session)
    elif setup_db == "Dynamic":
        drop_all_tables()
        create_db_and_tables()
    elif setup_db == "Production":
        create_db_and_tables()
        print("production db configured")
    yield


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:3000/registration",
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "token_type": "bearer"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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


@app.post("/registration")
def registration(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> str:
    print("Got registration")
    print(f"Username: {form_data.username}")
    print(f"Password: {form_data.password}")
    # see if username exists in database
    statement = select(FilmUser).where(FilmUser.username == form_data.username)
    current_user = session.exec(statement).first()
    if current_user:
        print("User found")
        raise HTTPException(status_code=404, detail="User Found Please Login")
    # make new user and commit data with password hash
    new_user = FilmUser(username=form_data.username, password=pwd_context.hash(
        form_data.password), date_registered=datetime.datetime.now(), profiles=[])
    session.add(new_user)
    session.commit()
    statement = select(FilmUser).where(FilmUser.username == form_data.username)
    current_user = session.exec(statement).first()
    # get info for token
    data_token = TokenModel(id=current_user.id, profiles=[])
    data_token = data_token.model_dump()
    # send back token
    return create_jwt_token(data_token)


@app.post("/login")
def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    print("Got login")
    print(f"Username: {form_data.username}")
    print(f"Password: {form_data.password}")
    # see if username exists in database
    statement = select(FilmUser).where(FilmUser.username == form_data.username)
    current_user = session.exec(statement).first()
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # verify password
    if not pwd_context.verify(form_data.password, current_user.password):
        raise HTTPException(status_code=404, detail="Wrong Password")
    # get info for token
    # send back token


@app.post("/addprofile")
def add_profile():
    pass


@app.post("/removeprofile")
def remove_profile():
    pass
