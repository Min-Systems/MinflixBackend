import datetime
from fastapi import HTTPException, status
from jose import jwt, JWTError
from .db import *
from .config import Settings
from ..data.film_data import *
from ..data.example_data import *
from ..models.film_models import *
from ..models.film_token_models import *
from ..models.token_models import *
from ..models.user_models import *

settings = Settings()


def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(
        datetime.timezone.utc) + datetime.timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "token_type": "bearer"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_jwt_token(token: str) -> dict:
    try:
        # Decode the token and verify the signature using the secret key
        # The decode function also checks the expiration claim automatically
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        print(f"The payload: {payload}")
        return payload

    except JWTError as e:
        # This will catch issues like invalid signature, expired token, etc.
        print(f"JWT error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_filmuser(token: str = Depends(settings.oauth2_scheme)) -> int:
    session_data = verify_jwt_token(token)
    return session_data.get("id")

UserDep = Annotated[int, Depends(get_current_filmuser)]