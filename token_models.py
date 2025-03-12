from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from pydantic import BaseModel
from user_models import *


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    '''
        id: this the film user id
        profiles: list of user profiles
    '''
    id: int
    profiles: List["ProfileData"]


class ProfileData(BaseModel):
    id: int
    displayname: str


'''
class TokenUserData(BaseModel):
    id: int
    profiles: List["ProfileData"]


class TokenData(BaseModel):
    token_user: TokenUserData
'''
