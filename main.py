import os
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.middleware.cors import CORSMiddleware
import uvicon


class Film(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


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
    # make the films as data representations for the db
    films = []
    for x in range(10):
        films.append(Film(name=f"film_{x+1}"))
    # use the session and commit them to the db
    for film in films:
        session.add(film)
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
    "https://minflixhd.web.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/films", response_model=list[Film])
def read_all_films(session: SessionDep, offset: int = 0):
    films = session.exec(select(Film).offset(offset)).all()
    return films

@app.get("/")
async def root():
    return {"message": "MinFlix Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
