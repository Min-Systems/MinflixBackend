from typing import List
from pydantic import BaseModel, ConfigDict
from user_models import *


class TokenModel(BaseModel):
    '''
        id: this the film user id
        profiles: list of user profiles
    '''
    id: int
    profiles: List["TokenProfileDataModel"]
    model_config = ConfigDict(from_attributes=True)


class TokenProfileDataModel(BaseModel):
    id: int
    displayname: str
    watch_later: List["TokenWatchLaterDataModel"]
    model_config = ConfigDict(from_attributes=True)


class TokenWatchLaterDataModel(BaseModel):
    id: int
    film_id: int
    model_config = ConfigDict(from_attributes=True)
