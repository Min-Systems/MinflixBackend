import os
import logging
import traceback
from contextlib import asynccontextmanager
from typing import Annotated, List
from fastapi import Depends, FastAPI, Response, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.orm import selectinload
from fastapi.middleware.cors import CORSMiddleware
from film_models import *
from user_models import *
from example_data import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables for database connection
db_user = os.getenv("DB_USER", "watcher")
db_password = os.getenv("DB_PASSWORD", "T:->%I-iMQXOiqOt")
db_name = os.getenv("DB_NAME", "filmpoc")
instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME", "minflix-451300:us-west2:streaming-db")

# Connection string for Cloud SQL
database_url = f"postgresql+pg8000://{db_user}:{db_password}@/{db_name}?unix_sock=/cloudsql/{instance_connection_name}/.s.PGSQL.5432"
logger.info(f"Using database URL: {database_url.replace(db_password, '********')}")

try:
    engine = create_engine(database_url, echo=True, pool_pre_ping=True)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    logger.error(traceback.format_exc())
    # don't raise, allow app to start anyway

def get_session():
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Database connection error")


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        logger.error(traceback.format_exc())
        # don't raise


def create_example_data(session: SessionDep):
    try:
        # Check if data already exists to avoid duplicates
        existing_films = session.exec(select(Film)).all()
        if not existing_films:
            for film in EXAMPLEFILMS:
                session.add(film)
            
        existing_users = session.exec(select(FilmUser)).all()
        if not existing_users:
            for user in EXAMPLEUSERS:
                session.add(user)
                
        session.commit()
        logger.info("Example data created successfully")
    except Exception as e:
        logger.error(f"Failed to create example data: {str(e)}")
        logger.error(traceback.format_exc())
        session.rollback()
        # Don't raise here to allow app to continue


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database but continue if it fails
    try:
        create_db_and_tables()
        with Session(engine) as session:
            create_example_data(session)
    except Exception as e:
        logger.error(f"Startup database initialization failed: {str(e)}")
        logger.error(traceback.format_exc())
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/films", response_model=List[FilmRead])
def read_all_films(session: SessionDep):
    try:
        statement = select(Film).options(
            selectinload(Film.film_cast),
            selectinload(Film.production_team)
        )
        films = session.exec(statement).all()
        
        # Modify the result to add a "name" field for backward compatibility
        for film in films:
            film.name = film.title  # Add name field to match frontend expectations
            
        logger.info(f"Retrieved {len(films)} films")
        return films
    except Exception as e:
        logger.error(f"Error retrieving films: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to retrieve films from database")


@app.get("/users")
def read_all_users(session: SessionDep):
    try:
        statement = select(FilmUser)
        users = session.exec(statement).all()

        data = ""
        for user in users:
            data += f"id: {user.id}, email: {user.email}, password: {user.password}, date_registered: {user.date_registered}\n"
            for profile in user.profiles:
                data += f"displayname: {profile.displayname}\n"
                for search in profile.search_history:
                    data += f"search_query: {search.search_query}\n"
                for favorite in profile.favorites:
                    data += f"favorite: {favorite.favorited_date} film_id: {favorite.film_id}\n"
                for watchlater in profile.watch_later:
                    data += f"dateadded: {watchlater.dateadded} film_id: {watchlater.film_id}\n"
                for watchhistory in profile.watch_history:
                    data += f"datewatched: {watchhistory.datewatched} film_id: {watchhistory.film_id}\n"

        logger.info("Retrieved user data")
        return Response(content=data)
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to retrieve users from database")
        

@app.get("/")
async def root():
    return {"message": "MinFlix Backend is running"}


@app.get("/health")
async def health_check():
    try:
        # Test database connection
        with Session(engine) as session:
            film_count = session.exec(select(Film)).count()
            return {
                "status": "healthy",
                "database": "connected",
                "film_count": film_count
            }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }