from typing import List
from pydantic import BaseModel, ConfigDict
from film_models import *


class FilmToken(BaseModel):
    id: int
    title: str
    image_name: str
    file_name: str
