from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

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
        films.append(Film(name=f"film_{x}"))
    # use the session and commit them to the db
    for film in films:
        session.add(film)
    session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        create_example_data(session)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/films",response_model=list[Film])
def read_all_films(session: SessionDep, offset: int = 0):
    films = session.exec(select(Film).offset(offset)).all()
    return films 
