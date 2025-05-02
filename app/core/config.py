import os
from pathlib import (Path)
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
        Settings class to configure backend

        Contains environment variables and global variables

        Attributes:
            db_setup (str): variable to control whether the database is reset at startup [Dynamic, Production, Example]
            db_url (str): connection url for database
            static_media_directory (str): directory for static media
            secret_key (str): the secret key to encode and decode jwt's
            algorithm (str): used to encode and decode jwt's
            access_token_expire_minutes (int): the number of minutes for the token to live
            images_dir (Path): path to the images
            films_dir (Path): path to the films
            chunk_size (int): chunk size to send the film part
            oauth2_scheme (OAuth2PasswordBearer): the default url to get tokens
            pwd_context (CryptContext): algorithm and context to encrypt passwords
    """
    db_setup: str = os.getenv("DATABASE_SETUP", "Dynamic")
    db_url: str = os.getenv(
        "DATABASE_URL", "postgresql://watcher:films@localhost/filmpoc")
    static_media_directory: str = os.getenv("MEDIA_DIRECTORY", "")
    recommender_file_directory: str = os.getenv("RECOMMENDER_DIRECTORY", "")
    secret_key: str = os.getenv(
        "SECRET_KEY", "80ebfb709b4ffc7acb52167b42388165d688a1035a01dd5dcf54990ea0faabe8")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10"))
    images_dir: Path = Path(f"{static_media_directory}/images")
    films_dir: Path = Path(f"{static_media_directory}/films")
    recommender_dir: Path = Path(f"{recommender_file_directory}/artifacts")
    chunk_size: int = 64*1024
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="login")
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")