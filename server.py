import os
import datetime
import secrets
from contextlib import asynccontextmanager
from typing import Annotated, List
from fastapi import Depends, FastAPI, Response, Form, HTTPException, status
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy import inspect, MetaData, Table
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
password_postgresql = "T:->%I-iMQXOiqOt"
instance_connection_name = "minflix-451300:us-west2:streaming-db"
url_postgresql = f"postgresql+psycopg2://{user_postgresql}:{password_postgresql}@/{db_postgresql}?host=/cloudsql/{instance_connection_name}"
engine = create_engine(url_postgresql, echo=True)


# openssl rand -hex 32 to generate key(more on this later)
SECRET_KEY = "20404ba49993ee4b5af02b141b14b4fdd2d06ff3f855f84a35113c4d890c0b13"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
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
    setup_db = "Production"
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
    "https://minflixhd.web.app",
    "https://minflixbackend-611864661290.us-west2.run.app",
    "https://minflixbackend-611864661290.us-west2.run.app/registration"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", 
                  "Access-Control-Allow-Origin", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
    max_age=600,
)


def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(
        datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "token_type": "bearer"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str) -> dict:
    try:
        # Decode the token and verify the signature using the secret key
        # The decode function also checks the expiration claim automatically
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"The payload: {payload}")
        return payload

    except JWTError as e:
        # This will catch issues like invalid signature, expired token, etc.
        print(f"JWT error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


@app.get("/")
async def root():
    return {
        "message": "MinFlix API is running",
        "version": "1.0",
        "endpoints": [
            "/login", 
            "/registration", 
            "/addprofile", 
            "/health",
            "/schema"
        ]
    }

@app.get("/schema")
async def inspect_schema():
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        schema_info = {}
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            schema_info[table_name] = [
                {"name": col["name"], "type": str(col["type"])} 
                for col in columns
            ]
        
        return {
            "tables": tables,
            "schema": schema_info
        }
    except Exception as e:
        return {
            "error": str(e)
        }

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Try a simpler health check that doesn't rely on specific tables
        with engine.connect() as conn:
            result = conn.execute("SELECT 1").fetchone()
            connected = result is not None
        
        return {
            "status": "healthy" if connected else "unhealthy",
            "database": "connected" if connected else "disconnected",
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }



@app.post("/registration")
async def registration(
    session: SessionDep, 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> str:
    try:
        # Check if user already exists
        print(f"Checking for existing user: {form_data.username}")
        statement = select(FilmUser).where(FilmUser.username == form_data.username)
        current_user = session.exec(statement).first()
        
        if current_user:
            print(f"User found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User already exists. Please login instead."
            )

        # Create new user
        print(f"Creating new user: {form_data.username}")
        hashed_password = pwd_context.hash(form_data.password)
        new_user = FilmUser(
            username=form_data.username, 
            password=hashed_password, 
            date_registered=datetime.datetime.now(), 
            profiles=[]
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        # Create token with user data
        data_token = TokenModel(id=new_user.id, profiles=[])
        data_token = data_token.model_dump()
        the_token = create_jwt_token(data_token)
        
        return the_token
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a generic message
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@app.post("/login")
async def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> str:
    statement = select(FilmUser).where(FilmUser.username == form_data.username)
    current_user = session.exec(statement).first()
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(form_data.password, current_user.password):
        raise HTTPException(status_code=404, detail="Wrong Password")

    profile_data = []
    for profile in current_user.profiles:
        profile_data.append(TokenProfileDataModel(
            id=profile.id, displayname=profile.displayname))

    data_token = TokenModel(id=current_user.id, profiles=profile_data)
    data_token = data_token.model_dump()
    the_token = create_jwt_token(data_token)
    return the_token


async def get_current_filmuser(token: str = Depends(oauth2_scheme)) -> int:
    print(f"[INFO]: GET CURRENT FILMUSER TOKEN: {token}")
    print(f"Type of token {type(token)}")
    session_data = verify_jwt_token(token)
    return session_data.get("id")


@app.post("/addprofile")
async def add_profile(displayname: Annotated[str, Form()], session: SessionDep, current_filmuser: Annotated[int, Depends(get_current_filmuser)]) -> str:
    current_user = session.get(FilmUser, current_filmuser)
    current_user.profiles.append(Profile(displayname=displayname))
    session.add(current_user)
    session.commit()

    # check to see if we can just use the session user already
    current_user = session.get(FilmUser, current_filmuser)
    profile_data = []
    for profile in current_user.profiles:
        profile_data.append(TokenProfileDataModel(
            id=profile.id, displayname=profile.displayname))

    data_token = TokenModel(id=current_user.id, profiles=profile_data)
    data_token = data_token.model_dump()
    the_token = create_jwt_token(data_token)

    return the_token


@app.post("/removeprofile")
def remove_profile():
    print("Got remove")