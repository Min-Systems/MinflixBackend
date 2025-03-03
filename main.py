import os
import logging
import traceback
from contextlib import asynccontextmanager
from typing import Annotated, List, Dict, Any
from fastapi import Depends, FastAPI, Response, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select, Field
from sqlalchemy.orm import selectinload
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

def drop_all_tables():
    """Drop all tables from the database"""
    try:
        SQLModel.metadata.drop_all(engine)
        logger.info("All tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to drop tables: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        logger.error(traceback.format_exc())
        return False

# Import models after engine is created but before creating tables
from film_models import *
from user_models import *
from example_data import *

def create_example_data(session: SessionDep):
    try:
        # Add example films
        logger.info("Adding example films...")
        for film in EXAMPLEFILMS:
            session.add(film)
            
        # Add example users
        logger.info("Adding example users...")
        for user in EXAMPLEUSERS:
            session.add(user)
            
        session.commit()
        logger.info("Example data created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create example data: {str(e)}")
        logger.error(traceback.format_exc())
        session.rollback()
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Only create tables on startup, don't reset automatically
        create_db_and_tables()
        with Session(engine) as session:
            # Check if we need to add example data
            films = session.exec(select(Film)).all()
            if not films:
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

@app.get("/reset-database")
async def reset_database():
    """Reset the entire database - drop all tables and recreate them with example data"""
    try:
        # Drop all tables
        if not drop_all_tables():
            return {"status": "error", "message": "Failed to drop tables"}
            
        # Create tables
        if not create_db_and_tables():
            return {"status": "error", "message": "Failed to create tables"}
            
        # Add example data
        with Session(engine) as session:
            if not create_example_data(session):
                return {"status": "error", "message": "Failed to add example data"}
            
        return {"status": "success", "message": "Database reset successfully"}
    except Exception as e:
        logger.error(f"Database reset failed: {str(e)}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": f"Failed to reset database: {str(e)}"}

@app.get("/films", response_model=List[Film])
async def read_all_films(session: SessionDep):
    try:
        # Try to use the Film model with all expected fields
        statement = select(Film).options(
            selectinload(Film.film_cast),
            selectinload(Film.production_team)
        )
        films = session.exec(statement).all()
        
        # Make sure films have a name field (compatibility with frontend)
        for film in films:
            # Set name from title if not present
            if not hasattr(film, "name") or film.name is None:
                film.name = film.title
                
        logger.info(f"Retrieved {len(films)} films")
        return films
    except Exception as e:
        logger.error(f"Error retrieving films: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve films: {str(e)}")

@app.get("/users")
async def read_all_users(session: SessionDep):
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

        return Response(content=data)
    except Exception as e:
        logger.error(f"Error in users endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error in users endpoint: {str(e)}")

@app.get("/db-test")
async def test_db():
    """Test database connection and table structure"""
    try:
        # Test basic connection
        with Session(engine) as session:
            result = session.execute("SELECT 1").fetchone()
            
            # Get table info
            tables_info = {}
            for table in SQLModel.metadata.tables.keys():
                try:
                    # Try to get columns for each table
                    columns = session.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'").fetchall()
                    tables_info[table] = [col[0] for col in columns]
                except Exception as table_error:
                    tables_info[table] = f"Error: {str(table_error)}"
            
            return {
                "status": "Connected",
                "basic_query": result,
                "tables": tables_info
            }
    except Exception as e:
        return {
            "status": "Failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

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