import os
import logging
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Film(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


db_user = os.getenv("DB_USER", "watcher")
db_password = os.getenv("DB_PASSWORD", "T:->%I-iMQXOiqOt")
db_name = os.getenv("DB_NAME", "filmpoc")
instance_connection_name = os.getenv("minflix-451300:us-west2:streaming-db")

# Connection string for Cloud SQL
database_url = f"postgresql+pg8000://{db_user}:{db_password}@/{db_name}?unix_sock=/cloudsql/{instance_connection_name}/.s.PGSQL.5432"
try:
    engine = create_engine(database_url, echo=True)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

def get_session():
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        raise


def create_example_data(session: Session):
    try:
        # Check if data already exists
        existing_films = session.exec(select(Film)).all()
        if existing_films:
            logger.info("Example data already exists")
            return

        # Create example films
        films = [
            Film(name="The Great Train Robbery (1903)"),
            Film(name="Nosferatu (1922)"),
            Film(name="The Cabinet of Dr. Caligari (1920)"),
            Film(name="Metropolis (1927)"),
            Film(name="The General (1926)"),
            Film(name="Safety Last! (1923)"),
            Film(name="The Kid (1921)"),
            Film(name="The Gold Rush (1925)"),
            Film(name="The Phantom of the Opera (1925)"),
            Film(name="The Lost World (1925)")
        ]
        
        for film in films:
            session.add(film)
        session.commit()
        logger.info("Example data created successfully")
    except Exception as e:
        logger.error(f"Failed to create example data: {str(e)}")
        session.rollback()
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_db_and_tables()
        with Session(engine) as session:
            create_example_data(session)
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    yield


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "https://minflixhd.web.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/films", response_model=list[Film])
async def read_all_films(session: SessionDep):
    try:
        films = session.exec(select(Film)).all()
        logger.info(f"Retrieved {len(films)} films")
        return films
    except Exception as e:
        logger.error(f"Error retrieving films: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to retrieve films from database")
        
@app.get("/")
async def root():
    return {"message": "MinFlix Backend is running"}

@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS is working!"}

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
