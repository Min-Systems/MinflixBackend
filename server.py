import os
import datetime
from contextlib import asynccontextmanager
from typing import Annotated, List
from fastapi import Depends, FastAPI, Response, Form, HTTPException, status
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.orm import selectinload
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
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
ACCESS_TOKEN_EXPIRE_MINUTES = 5
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
        print(f"{setup_db} db configured")
    elif setup_db == "Dynamic":
        drop_all_tables()
        create_db_and_tables()
        print(f"{setup_db} db configured")
    elif setup_db == "Production":
        create_db_and_tables()
        print(f"{setup_db} db configured")
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


def verify_jwt_token(token: str) -> dict:
    try:
        # Decode the token and verify the signature using the secret key
        # The decode function also checks the expiration claim automatically
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check if it's a bearer token
        if payload.get("token_type") != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return payload

    except JWTError:
        # This will catch issues like invalid signature, expired token, etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


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
    print("The data token:")
    print(data_token)
    # send back token
    return create_jwt_token(data_token)


@app.post("/login")
def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> str:
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
    data_token = TokenModel(id=current_user.id, profiles=[])
    data_token = data_token.model_dump()
    print("The data token:")
    print(data_token)
    # send back token
    return create_jwt_token(data_token)


def get_current_filmuser(token: str = Depends(oauth2_scheme)) -> int:
    session_data = verify_jwt_token(token)
    return session_data.get("id")


@app.post("/addprofile")
def add_profile(displayname: Annotated[str, Form()], session: SessionDep, current_filmuser: int = Depends(get_current_filmuser)) -> str:
    current_user = session.get(FilmUser, current_filmuser) 
    current_user.profiles.append(Profile(displayname=displayname))
    session.commit(current_user)
    current_user = session.get(FilmUser, current_filmuser) 

    profile_data = []
    for profile in current_user.profiles:
        profile_data.append(TokenProfileDataModel(id=profile.id, displayname=profile.displayname))

    data_token = TokenModel(id=current_user.id, profiles=profile_data) 
    data_token = data_token.model_dump()
    print("The data token:")
    print(data_token)
    # send back token
    return create_jwt_token(data_token)


@app.post("/removeprofile")
def remove_profile():
    pass
