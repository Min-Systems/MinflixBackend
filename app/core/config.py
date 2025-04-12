import os
from pathlib import Path
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_setup: str = os.getenv("DATABASE_SETUP", "Dynamic")
    db_url: str = os.getenv(
        "DATABASE_URL", "postgresql://watcher:films@localhost/filmpoc")
    static_media_directory: str = os.getenv("MEDIA_DIRECTORY", "")
    secret_key: str = os.getenv(
        "SECRET_KEY", "80ebfb709b4ffc7acb52167b42388165d688a1035a01dd5dcf54990ea0faabe8")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10"))
    images_dir: Path = Path(f"{static_media_directory}/images")
    films_dir: Path = Path(f"{static_media_directory}/films")
    chunk_size: int = 1024*1024
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="login")
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
