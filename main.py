import os
import logging
import traceback
from contextlib import asynccontextmanager
from typing import Annotated, List, Dict, Any
from fastapi import Depends, FastAPI, Response, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.orm import selectinload
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define a simple Film model that matches main.py
# This is for backward compatibility
class Film(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

# Import the rest of the models afterward to prevent import errors
from sqlmodel import Field

# Get environment variables for database connection
db_user = os.getenv("DB_USER", "watcher")
db_password = os.getenv("DB_PASSWORD", "T:->%I-iMQXOiqOt")
db_name = os.getenv("DB_NAME", "filmpoc")
instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME", "minflix-451300:us-west2:streaming-db")

# Connection string for Cloud SQL
database_url = f"postgresql+pg8000://{db_user}:{db_password}@/{db_name}?unix_sock=/cloudsql/{instance_connection_name}/.s.PGSQL.5432"
logger.info(f"Using database URL: {database_url.replace(db_password, '********')}")

try:
    # Enable echo to see all SQL queries
    engine = create_engine(database_url, echo=True, pool_pre_ping=True)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    logger.error(traceback.format_exc())
    # don't raise

def get_session():
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

SessionDep = Annotated[Session, Depends(get_session)]

def create_db_and_tables():
    try:
        # Just create the simple Film model table for now
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        logger.error(traceback.format_exc())

def create_example_data(session: Session):
    try:
        # Check if data already exists
        existing_films = session.exec(select(Film)).all()
        if existing_films:
            logger.info(f"Example data already exists, found {len(existing_films)} films")
            return

        # Create example films - simplified version like in main.py
        films = [
            Film(name="The Great Train Robbery (1903)"),
            Film(name="Nosferatu (1922)"),
            Film(name="The Cabinet of Dr. Caligari (1920)"),
            Film(name="Metropolis (1927)"),
            Film(name="The General (1926)")
        ]
        
        for film in films:
            session.add(film)
        session.commit()
        logger.info("Example data created successfully")
    except Exception as e:
        logger.error(f"Failed to create example data: {str(e)}")
        logger.error(traceback.format_exc())
        session.rollback()

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    allow_origins=["https://minflixhd.web.app", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.get("/films", response_model=list[Film])
async def read_all_films(session: SessionDep):
    try:
        # Simplify to match main.py approach
        films = session.exec(select(Film)).all()
        logger.info(f"Retrieved {len(films)} films")
        return films
    except Exception as e:
        logger.error(f"Error retrieving films: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve films: {str(e)}")

@app.get("/users")
async def read_all_users(session: SessionDep):
    try:
        # First try to select from Film table as a test
        test_films = session.exec(select(Film)).all()
        film_count = len(test_films)
        
        # Return a simple test message for debugging
        return Response(
            content=f"Database connection test successful. Found {film_count} films.\n\n"
                    f"No users table implemented yet, but database connection is working."
        )
    except Exception as e:
        logger.error(f"Error in users endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error in users endpoint: {str(e)}")

@app.get("/")
async def root():
    return {"message": "MinFlix Backend is running"}

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        with Session(engine) as session:
            try:
                # Check if Film table exists
                film_count = session.exec(select(Film)).count()
                db_status = "connected"
            except Exception as e:
                film_count = 0
                db_status = f"table error: {str(e)}"
                
        return {
            "status": "healthy",
            "database": db_status,
            "film_count": film_count,
            "environment": {
                "instance_name": instance_connection_name,
                "db_name": db_name,
                "db_user": db_user
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)