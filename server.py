import os
import datetime
import base64
import secrets
from contextlib import asynccontextmanager
from typing import Annotated, List, Optional
from fastapi import Depends, FastAPI, Response, Form, HTTPException, Cookie
from sqlmodel import Session, SQLModel, create_engine, select
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

# Session model for tracking user sessions
class UserSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="filmuser.id")
    session_token: str = Field(unique=True)
    active_profile_id: Optional[int] = Field(default=None, foreign_key="profile.id")
    created_at: datetime.datetime
    expires_at: datetime.datetime

# Helper function to generate a session token
def generate_session_token():
    return secrets.token_hex(32)

# Helper function to verify session
def verify_session(session_token: str = Cookie(None), session: Session = Depends(get_session)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find active session
    db_session = session.exec(
        select(UserSession)
        .where(UserSession.session_token == session_token)
        .where(UserSession.expires_at > datetime.datetime.now())
    ).first()
    
    if not db_session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    
    # Return user_id from the session
    return db_session

# Login endpoint
@app.post("/login")
def login(
    response: Response, 
    session: SessionDep,
    email: Annotated[str, Form()], 
    password: Annotated[str, Form()]
):
    # Find user with matching email and password
    user = session.exec(
        select(FilmUser)
        .where(FilmUser.email == email)
        .where(FilmUser.password == password)
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create a new session
    session_token = generate_session_token()
    created_at = datetime.datetime.now()
    expires_at = created_at + datetime.timedelta(days=7)  # Session valid for 7 days
    
    # Store session in database
    user_session = UserSession(
        user_id=user.id,
        session_token=session_token,
        created_at=created_at,
        expires_at=expires_at
    )
    session.add(user_session)
    session.commit()
    
    # Set the session cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="Lax",
        expires=expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
    )
    
    return {"message": "Login successful", "user_id": user.id}

# Registration endpoint (update the existing one)
@app.post("/registration")
def registration(
    response: Response, 
    session: SessionDep, 
    email: Annotated[str, Form()], 
    password: Annotated[str, Form()]
):
    # Check if user already exists
    existing_user = session.exec(select(FilmUser).where(FilmUser.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    current_date = datetime.datetime.now()
    new_user = FilmUser(email=email, password=password,
                        date_registered=str(current_date), profiles=[])
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Create a session for the new user
    session_token = generate_session_token()
    expires_at = current_date + datetime.timedelta(days=7)
    
    user_session = UserSession(
        user_id=new_user.id,
        session_token=session_token,
        created_at=current_date,
        expires_at=expires_at
    )
    session.add(user_session)
    session.commit()
    
    # Set the session cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="Lax",
        expires=expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
    )
    
    return {"message": "Registration successful", "user_id": new_user.id}

# Logout endpoint
@app.post("/logout")
def logout(
    response: Response, 
    session: SessionDep,
    user_session: UserSession = Depends(verify_session)
):
    # Remove session from database
    session.delete(user_session)
    session.commit()
    
    # Clear cookie
    response.delete_cookie(key="session_token")
    
    return {"message": "Logged out successfully"}

# Get user profiles
@app.get("/user-profiles")
def get_user_profiles(
    session: SessionDep,
    user_session: UserSession = Depends(verify_session)
):
    # Get user
    user = session.get(FilmUser, user_session.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Load profiles
    profiles = session.exec(
        select(Profile)
        .where(Profile.filmuserid == user.id)
    ).all()
    
    return {"profiles": [{"id": p.id, "displayname": p.displayname} for p in profiles]}

# Create profile
@app.post("/create-profile")
def create_profile(
    profile_data: dict,
    session: SessionDep,
    user_session: UserSession = Depends(verify_session)
):
    displayname = profile_data.get("displayname")
    if not displayname:
        raise HTTPException(status_code=400, detail="Display name is required")
    
    # Get user
    user = session.get(FilmUser, user_session.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create profile
    new_profile = Profile(
        filmuserid=user.id,
        displayname=displayname,
        search_history=[],
        favorites=[],
        watch_later=[],
        watch_history=[]
    )
    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)
    
    return {"message": "Profile created successfully", "profile_id": new_profile.id}

# Select profile
@app.post("/select-profile")
def select_profile(
    profile_data: dict,
    session: SessionDep,
    user_session: UserSession = Depends(verify_session)
):
    profile_id = profile_data.get("profile_id")
    if not profile_id:
        raise HTTPException(status_code=400, detail="Profile ID is required")
    
    # Verify the profile belongs to the user
    profile = session.exec(
        select(Profile)
        .where(Profile.id == profile_id)
        .where(Profile.filmuserid == user_session.user_id)
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found or not authorized")
    
    # Update active profile in session
    user_session.active_profile_id = profile.id
    session.add(user_session)
    session.commit()
    
    return {"message": "Profile selected successfully"}

# Get current profile
@app.get("/current-profile")
def get_current_profile(
    session: SessionDep,
    user_session: UserSession = Depends(verify_session)
):
    if not user_session.active_profile_id:
        raise HTTPException(status_code=400, detail="No active profile selected")
    
    profile = session.get(Profile, user_session.active_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "profile": {
            "id": profile.id,
            "displayname": profile.displayname
        }
    }