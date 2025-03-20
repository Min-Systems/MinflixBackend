from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, ValidationError
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

    model_config = ConfigDict(from_attributes=True)