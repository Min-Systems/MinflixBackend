import os
import datetime
import secrets
from contextlib import asynccontextmanager
from typing import Annotated, List
from fastapi import Depends, FastAPI, Response, Form, HTTPException, status
from sqlmodel import Session, SQLModel, create_engine, select, Field
from sqlalchemy import inspect, MetaData, Table, Column, String
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


# Create a custom FilmUser class that maps username to email
# This overrides the imported one but maintains compatibility with existing code
class FilmUser(SQLModel, table=True):
    __tablename__ = "filmuser"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column("email", String))  # Map username to email column
    password: str
    date_registered: datetime.datetime
    profiles: List["Profile"] = Relationship(back_populates="filmuser")


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
        # In production, don't recreate tables but do test connection
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print(f"{setup_db} db connection verified")
        except Exception as e:
            print(f"Error connecting to database: {e}")
    yield


app = FastAPI(lifespan=lifespan)


origins = [
    "https://minflixhd.web.app",  # Remove trailing slash
    "http://localhost:3000",
    "https://minflixbackend-611864661290.us-west2.run.app"
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
            "/schema",
            "/test-auth"
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


# Test endpoint for frontend to verify auth works
@app.get("/test-auth")
async def test_auth(current_filmuser: Annotated[int, Depends(get_current_filmuser)]):
    return {"authenticated": True, "user_id": current_filmuser}


@app.post("/registration")
async def registration(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> str:
    try:
        # Debug log
        print(f"Registration attempt for username: {form_data.username}")
        
        statement = select(FilmUser).where(FilmUser.username == form_data.username)
        current_user = session.exec(statement).first()
        if current_user:
            print("User found")
            raise HTTPException(status_code=404, detail="User Found Please Login")

        new_user = FilmUser(username=form_data.username, password=pwd_context.hash(
            form_data.password), date_registered=datetime.datetime.now(), profiles=[])
        session.add(new_user)
        session.commit()
        
        # Debug log
        print(f"User created with ID: {new_user.id}")
        
        # check if we need to actually requery database, we have it in the session
        statement = select(FilmUser).where(FilmUser.username == form_data.username)
        current_user = session.exec(statement).first()

        data_token = TokenModel(id=current_user.id, profiles=[])
        data_token = data_token.model_dump()
        the_token = create_jwt_token(data_token)
        return the_token
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@app.post("/login")
async def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> str:
    try:
        # Debug log
        print(f"Login attempt for username: {form_data.username}")
        
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
        
        # Debug log
        print(f"Login successful for user ID: {current_user.id}")
        
        return the_token
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")


async def get_current_filmuser(token: str = Depends(oauth2_scheme)) -> int:
    print(f"[INFO]: GET CURRENT FILMUSER TOKEN: {token}")
    print(f"Type of token {type(token)}")
    session_data = verify_jwt_token(token)
    return session_data.get("id")


@app.post("/addprofile")
async def add_profile(displayname: Annotated[str, Form()], session: SessionDep, current_filmuser: Annotated[int, Depends(get_current_filmuser)]) -> str:
    try:
        # Debug log
        print(f"Adding profile '{displayname}' for user ID: {current_filmuser}")
        
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
        
        # Debug log
        print(f"Profile added successfully, token generated")
        
        return the_token
    except Exception as e:
        print(f"Add profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Add profile error: {str(e)}")


@app.post("/removeprofile")
def remove_profile():
    print("Got remove")