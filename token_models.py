<<<<<<< HEAD
from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from pydantic import BaseModel
=======
from typing import List
from pydantic import BaseModel, ConfigDict
>>>>>>> develop
from user_models import *


class TokenModel(BaseModel):
    '''
        id: this the film user id
        profiles: list of user profiles
    '''
    id: int
    profiles: List["TokenProfileDataModel"]
<<<<<<< HEAD
=======
    model_config = ConfigDict(from_attributes=True)
>>>>>>> develop


class TokenProfileDataModel(BaseModel):
    id: int
    displayname: str
<<<<<<< HEAD
=======
    watch_later: List["TokenWatchLaterDataModel"]
    favorites: List["TokenFavoriteDataModel"]
    model_config = ConfigDict(from_attributes=True)


class TokenWatchLaterDataModel(BaseModel):
    id: int
    film_id: int
    model_config = ConfigDict(from_attributes=True)

class TokenFavoriteDataModel(BaseModel):
    id: int
    film_id: int
    model_config = ConfigDict(from_attributes=True)
>>>>>>> develop
