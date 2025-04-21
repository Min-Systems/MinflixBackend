import datetime
import logging
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Header, Response, Depends, FastAPI, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pathlib import Path
from .core.db import *
from .core.jwt import *
from .core.db import *
from .core.log import *
from .core.recommender import recommend
from .core.config import Settings
from .data.film_data import *
from .data.example_data import *
from .models.film_models import *
from .models.film_token_models import *
from .models.token_models import *
from .models.user_models import *

settings = Settings()


logging.info(f"[INFO]: got media directory: {settings.static_media_directory}")
logging.info(f"[INFO]: got images directory: {settings.images_dir}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        This is the lifespace that controls startup and database configuration

        Parameters:
            app (FastAPI): the fastapi app that the lifecycle will bind to
    """
    with Session(engine) as session:
        print(f"Database setup mode: {settings.db_setup}")
        if settings.db_setup == "Example":
            drop_all_tables()
            create_db_and_tables()
            create_example_data(session)
            print(f"{settings.db_setup} db configured")
        elif settings.db_setup == "Dynamic":
            drop_all_tables()
            create_db_and_tables()
            print(f"{settings.db_setup} db configured")
        elif settings.db_setup == "Production":
            create_db_and_tables()
            print(f"{settings.db_setup} db configured")

        # check if one film is in the database
        statement = select(Film)
        films_present = session.exec(statement).first()
        if not films_present:
            add_films(session)
            print(f"[INFO]: added films")
        else:
            print(f"[INFO]: no films added")

    yield


app = FastAPI(lifespan=lifespan)


origins = [
    "https://minflixclient.pages.dev",
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


@app.get("/")
async def root():
    """
        This route just returns telemetry data

        Returns:
            dict: information about api
    """
    logging.info(f"[INFO]: got root route")
    return {
        "message": "MinFlix API is running",
        "version": "6.0",
        "environment": "production",
        "endpoints": [
            "/login",
            "/registration",
            "/addprofile",
            "/editprofile",
            "/watchlater",
            "/favorite",
            "/watchhistory",
            "/getfilms",
            "/film",
            "/images"
        ]
    }


@app.post("/registration")
async def registration(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> str:
    """
        This is the registration endpoint where users can make an account

        Parameters:
            session (SessionDep): this is the database session
            form_data (OAuth2PasswordRequestForm): this is the formdata from the frontend form

        Returns:
            str: the jwt token that represents the new state after edits
    """
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
        hashed_password = settings.pwd_context.hash(form_data.password)
        new_user = FilmUser(
            username=form_data.username,
            password=hashed_password,
            date_registered=datetime.datetime.now(),
            profiles=[],
            watch_later=[],
            watch_history=[],
            favorites=[]
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return create_jwt_token(TokenModel.model_validate(new_user).model_dump())

    # Catch errors
    except JWTError:
        raise HTTPException(
            status_code=401,  # Unauthorized
            detail=f"Invalid JWT token: {str(JWTError)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"Registration failed: {str(e)}"
        )


@app.post("/login")
async def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> str:
    """
        This is the login endpoint where the user can login and receive a state/authentication token
    
        Parameters:
            session (SessionDep): this is the database session
            form_data (OAuth2PasswordRequestForm): this is the formdata from the frontend form

        Returns:
            str: the jwt token that represents the new state after edits
    """
    try:
        statement = select(FilmUser).where(
            FilmUser.username == form_data.username)
        current_user = session.exec(statement).first()

        if current_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if not settings.pwd_context.verify(form_data.password, current_user.password):
            raise HTTPException(status_code=404, detail="Wrong Password")

        return create_jwt_token(TokenModel.model_validate(current_user).model_dump())

    # Catch errors
    except JWTError:
        raise HTTPException(
            status_code=401,  # Unauthorized
            detail=f"Invalid JWT token: {str(JWTError)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"Login failed: {str(e)}"
        )


@app.post("/addprofile")
async def add_profile(displayname: Annotated[str, Form()], session: SessionDep, current_filmuser: UserDep) -> str:
    """
        This is the add profile endpoint that allows users to add a profile

        Parameters:
            displayname Annotated[str, Form()]: the displayname of the profile to add
            session SessionDep: this is the database session
            current_filmuser Annotated[int, Depends(get_current_filmuser)]: the profile currently making the request
        
        Returns:    
            str: the jwt token that represents the new state after edits
    """
    try:
        current_user = session.get(FilmUser, current_filmuser)
        current_user.profiles.append(Profile(displayname=displayname))

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return create_jwt_token(TokenModel.model_validate(current_user).model_dump())

    # Catch errors
    except JWTError:
        raise HTTPException(
            status_code=401,  # Unauthorized
            detail=f"Invalid JWT token: {str(JWTError)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"AddProfile failed: {str(e)}"
        )


@app.post("/editprofile")
async def edit_profile(displayname: Annotated[str, Form()], newdisplayname: Annotated[str, Form()], session: SessionDep, current_filmuser: UserDep) -> str:
    """
        This is the endpoint where the user can edit a profile

        Parameters: 
            displayname (Annotated[str, Form()]): the displayname of the profile to change
            newdisplayname (Annotated[str, Form()]): the displayname to change the profile to
            session (SessionDep): this is the database session
            current_filmuser (Annotated[int, Depends(get_current_filmuser)]): the current user making the request

        Returns:    
            str: the jwt token that represents the new state after edits
    """
    try:
        current_user = session.get(FilmUser, current_filmuser)

        # change the display name
        for profile in current_user.profiles:
            if profile.displayname == displayname:
                profile.displayname = newdisplayname
                break

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return create_jwt_token(TokenModel.model_validate(current_user).model_dump())

    # Catch errors
    except JWTError:
        raise HTTPException(
            status_code=401,  # Unauthorized
            detail=f"Invalid JWT token: {str(JWTError)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"Edit Profile failed: {str(e)}"
        )


@app.post("/watchlater/{profile_id}/{film_id}")
async def add_watch_later(profile_id: str, film_id: str, session: SessionDep, current_filmuser: UserDep) -> str:
    """
        This is the endpoint that allows the user to add a film to watch later

        Parameters:
            profile_id (str): the id of the profile to add the watch later to
            film_id (str): the id of the film to add to the watch later
            session (SessionDep): this is the database session
            current_filmuser (UserDep): the current user 

        Returns:    
            str: the jwt token that represents the new state after edits
    """
    try:
        current_user = session.get(FilmUser, current_filmuser)
        print(f"Got profile_id: {profile_id}")
        print(f"Got film_id: {film_id}")

        # get the profile inside the session
        for profile in current_user.profiles:
            if profile.id == int(profile_id):
                profile.watch_later.append(WatchLater(
                    profileid=int(profile_id), film_id=int(film_id)))
                break

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return create_jwt_token(TokenModel.model_validate(current_user).model_dump())

    # Catch errors
    except JWTError:
        raise HTTPException(
            status_code=401,  # Unauthorized
            detail=f"Invalid JWT token: {str(JWTError)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"Add Watch Later failed: {str(e)}"
        )


@app.post("/favorite/{profile_id}/{film_id}")
async def add_favorite(profile_id: str, film_id: str, session: SessionDep, current_filmuser: UserDep) -> str:
    """
        This is the endpoint that allows a user to add a favorite film

        Parameters:
            profile_id (str): the id of the profile to add the watch later to
            film_id (str): the id of the film to add to the watch later
            session (SessionDep): this is the database session
            current_filmuser (UserDep): the current user 
        
        Returns:    
            str: the jwt token that represents the new state after edits
    """
    try:
        current_user = session.get(FilmUser, current_filmuser)
        print(f"Got profile_id: {profile_id}")
        print(f"Got film_id: {film_id}")

        # get the profile inside the session
        for profile in current_user.profiles:
            if profile.id == int(profile_id):
                profile.favorites.append(
                    Favorite(profileid=int(profile_id), film_id=int(film_id)))
                break

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return create_jwt_token(TokenModel.model_validate(current_user).model_dump())

    # Catch errors
    except JWTError:
        raise HTTPException(
            status_code=401,  # Unauthorized
            detail=f"Invalid JWT token: {str(JWTError)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"Add Favorite failed: {str(e)}"
        )


@app.post("/add_watchhistory/{profile_id}/{film_id}")
async def add_watchhistory(profile_id: str, film_id: str, session: SessionDep, current_filmuser: UserDep) -> str:
    """
        This is the endpoint that allows a user to add a film to the their watch history

        Parameters:
            profile_id (str): the id of the profile to add the watch history to
            film_id (str): the id of the film to add to the watch history 
            session (SessionDep): this is the database session
            current_filmuser (UserDep): the current user 
        
        Returns:    
            str: the jwt token that represents the new state after edits
    """
    try:
        current_user = session.get(FilmUser, current_filmuser)

        # get the profile inside the session
        for profile in current_user.profiles:
            if profile.id == int(profile_id):
                profile.watch_history.append(
                    WatchHistory(profileid=int(profile_id), film_id=int(film_id)))
                break

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return create_jwt_token(TokenModel.model_validate(current_user).model_dump())

    # Catch errors
    except JWTError:
        raise HTTPException(
            status_code=401,  # Unauthorized
            detail=f"Invalid JWT token: {str(JWTError)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"Add Favorite failed: {str(e)}"
        )


@app.get("/getfilms")
async def get_film_list(session: SessionDep) -> list[FilmToken]:
    """
        This is the endpoint that allows a user to get the list of films to stream

        Parameters:
            session: SessionDep

        Returns:    
            str: the jwt token that represents the new state after edits
    """
    try:
        statement = select(Film)
        result = session.exec(statement).all()

        return result

    # Catch errors
    except JWTError:
        raise HTTPException(
            status_code=401,  # Unauthorized
            detail=f"Invalid JWT token: {str(JWTError)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"Get Films failed: {str(e)}"
        )


@app.get("/film/{film_name}")
async def stream_film(film_name: str, range: str = Header(None)):
    """
        This is the endpoint that allows a user to stream a film

        Parameters:
            film_name (str): the name of the film to stream
            range (str): the range of the film file to request

        Returns:    
            str: the jwt token that represents the new state after edits
    """
    try:
        start, end = range.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else start + settings.chunk_size

        # current_film = static_media_directory + "/EvilBrainFromOuterSpace_512kb.mp4"
        current_film = f"{settings.static_media_directory}/films/{film_name}"
        logging.info(f"[INFO]: got the file as: {current_film}")
        print(f"[INFO]: got the file as: {current_film}")
        current_film = Path(current_film)

        with open(current_film, "rb") as video:
            print(f"[INFO]: opened file")
            video.seek(start)
            data = video.read(end - start)
            filesize = str(current_film.stat().st_size)
            headers = {
                'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
                'Accept-Ranges': 'bytes'
            }

            return Response(data, status_code=206, headers=headers, media_type="video/mp4")

    except HTTPException:
        raise HTTPException(status_code=400, detail="Invalid film request")


@app.get("/images/{image_name}")
async def get_image(image_name: str):
    """
        This is the endpoint that allows a user to fetch an image 

        Parameters:
            image_name (str): the name of the image to fetch

        Returns:    
            str: the jwt token that represents the new state after edits
    """
    try:
        # Construct the intended path
        image_path = (settings.images_dir / f"{image_name}").resolve()
        logging.info(f"[INFO]: got resolved path {image_path}")

        # Critical security check - ensure the resolved path is within images_dir
        if not str(image_path).startswith(str(settings.images_dir.resolve())):
            logging.info(f"[SECURITY]: Attempted path traversal: {image_name}")
            raise HTTPException(status_code=403, detail="Access denied")

        image_path = (settings.images_dir / f"{image_name}").resolve()
        logging.info(f"[INFO]: image path gotten {image_path}")

        if not image_path.exists():
            logging.info(f"[INFO]: image not found")
            raise HTTPException(status_code=404, detail="Image not found")

        # Set cache headers (1 hour = 3600 seconds)
        headers = {"Cache-Control": "public, max-age=3600"}

        return FileResponse(
            path=str(image_path),
            headers=headers,
            # Determine media type from extension
            media_type=f"image/{image_path.suffix.lstrip('.')}"
        )

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image request")

@app.get("/recommendations/{profile_id}")
async def get_recommendations(profile_id: str, session: SessionDep, current_filmuser: UserDep):
    """
        This is the endpoint that shows the recommended films for a profile based on wathch history.

        Parameters:
            profile_id (str): the id of the profile to fetch the watch history
            session (SessionDep): this is the database session
            current_filmuser (UserDep): the current user
        
        Returns:
            list: the list of recommended films basded on watch history of the current profile
    """
    try:
        current_user = session.get(FilmUser, current_filmuser)

        selected_profile = None
        for profile in current_user.profiles:
            if profile.id == int(profile_id):
                selected_profile = profile
                break
        
        # Load all films
        statement = select(Film)
        films_list = session.exec(statement).all()
        films_dict = {film.id: film for film in films_list}

        # Get the last watched film title from profile watch history
        last_watched = selected_profile.watch_history[-1]
        watched_title = films_dict[last_watched.film_id].title

        # Get recommended movies using the recommend function
        recommended_titles = recommend(watched_title)
        # Map recommended movies to Film objects
        recommended_films = [film for film in films_list if film.title in recommended_titles]

        return recommended_films
    
    except Exception as e:
        raise HTTPException(
            status_code=500,  # Internal server error
            detail=f"Recommend Films failed: {str(e)}"
        )