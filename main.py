import os
import datetime
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy import inspect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pathlib import Path
from film_models import *
from user_models import *
from example_data import *
from token_models import *

# Localhost environment variables for local deployment
# Dockerfile has production environment variables
db_name = os.getenv("DB_NAME", "filmpoc")
db_user = os.getenv("DB_USER", "watcher")
db_password = os.getenv("DB_PASSWORD", "films")
db_host = os.getenv("DB_HOST", "")
instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME", "")
setup_db = os.getenv("SETUPDB", "Dynamic")
db_url = os.getenv("DB_URL", "")

# Log the connection envs
print("[INFO]: LOGGING CONNECTION ENV VALUES")
print(f"db_name = {db_name}")
print(f"db_user = {db_user}")
print(f"db_password = {db_password}")
print(f"db_host = {db_host}")
print(f"instance_connection_name = {instance_connection_name}")
print(f"setup_db = {setup_db}")

# Loads production database or local database
if instance_connection_name:
    # Google Cloud
    url_postgresql = f"postgresql+psycopg2://{db_user}:{db_password}@/{db_name}?host=/cloudsql/{instance_connection_name}"
    print(f"[INFO]: using google cloud with url: {url_postgresql}")
elif db_host or db_url:
    # Render.com
    url_postgresql = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
    url_postgresql = db_url
    print(f"[INFO]: using render with url: {url_postgresql}")
else:
    # Local
    url_postgresql = f"postgresql://{db_user}:{db_password}@localhost/{db_name}"
    print(f"[INFO]: using local with url: {url_postgresql}")

engine = create_engine(url_postgresql, echo=True)

# openssl rand -hex 32 to generate key(more on this later)
SECRET_KEY = os.getenv(
    "SECRET_KEY", "80ebfb709b4ffc7acb52167b42388165d688a1035a01dd5dcf54990ea0faabe8")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
IMAGES_DIR = Path("static/images")

# Log the crypt envs
print("[INFO]: LOGGING CRYPT ENVS")
print(f"SECRET_KEY = {SECRET_KEY}")
print(f"ALGORITHM = {ALGORITHM}")
print(f"ACCESS_TOKEN_EXPIRE_MINUTES = {ACCESS_TOKEN_EXPIRE_MINUTES}")


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
    # Get setup mode from environment variable (Dynamic is default)
    print(f"Database setup mode: {setup_db}")
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

    # Ensure images folder exists
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Images directory: {IMAGES_DIR.absolute()}")

    yield


app = FastAPI(lifespan=lifespan)


origins = [
    "https://minflixhd.web.app",
    "https://minflix-kzt6.onrender.com",
    "https://minflixfrontend.onrender.com/",
    "https://minflixclient-production.up.railway.app",
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
        "environment": "production" if instance_connection_name or db_host else "local",
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
            result = conn.execute(select(1)).fetchone()
            connected = result is not None

        return {
            "status": "healthy" if connected else "unhealthy",
            "database": "connected" if connected else "disconnected",
            "environment": "production" if instance_connection_name else "local",
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }


@app.post("/registration")
async def registration(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> str:
    try:
        statement = select(FilmUser).where(
            FilmUser.username == form_data.username)
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

        return create_jwt_token(TokenModel.model_validate(new_user).model_dump())

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

    return create_jwt_token(TokenModel.model_validate(current_user).model_dump())


async def get_current_filmuser(token: str = Depends(oauth2_scheme)) -> int:
    session_data = verify_jwt_token(token)
    return session_data.get("id")


@app.post("/addprofile")
async def add_profile(displayname: Annotated[str, Form()], session: SessionDep, current_filmuser: Annotated[int, Depends(get_current_filmuser)]) -> str:
    current_user = session.get(FilmUser, current_filmuser)
    current_user.profiles.append(Profile(displayname=displayname))

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return create_jwt_token(TokenModel.model_validate(current_user).model_dump())


@app.post("/editprofile")
async def edit_profile(displayname: Annotated[str, Form()], newdisplayname: Annotated[str, Form()], session: SessionDep, current_filmuser: Annotated[int, Depends(get_current_filmuser)]) -> str:
    current_user = session.get(FilmUser, current_filmuser)

    # change the display name
    for profile in current_user.profiles:
        if profile.displayname == displayname:
            profile.displayname = newdisplayname

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return create_jwt_token(TokenModel.model_validate(current_user).model_dump())


@app.post("/removeprofile")
def remove_profile():
    print("Got remove")


@app.post("/watchlater/{profile_id}/{film_id}")
async def add_watch_later(profile_id: int, film_id: int, session: SessionDep, current_filmuser: Annotated[int, Depends(get_current_filmuser)]):
    current_user = session.get(FilmUser, current_filmuser)
    print(f"Got profile_id: {profile_id}")
    print(f"Got film_id: {film_id}")
    # add the new watch_later
    # get the profile inside the session
    for profile in current_user:
        if profile.id == profile_id:
            pass


@app.get("/images/{image_name}")
async def get_image(image_name: str):
    # Sanitize the filename to prevent path traversal
    try:
        image_path = (IMAGES_DIR / f"{image_name}.jpg").resolve()
        print(f"[INFO]: image path gotten {image_path}")
        if not image_path.exists():
            print(f"[INFO]: image not found")
            raise HTTPException(status_code=404, detail="Image not found")

        # Set cache headers (1 hour = 3600 seconds)
        headers = {"Cache-Control": "public, max-age=3600"}

        return FileResponse(
            path=str(image_path),
            headers=headers,
            # Determine media type from extension
            media_type=f"image/{image_path.suffix.lstrip('.')}"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Invalid image request")
