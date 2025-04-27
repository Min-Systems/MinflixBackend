from pydantic import BaseModel
from .film_models import *


class FilmToken(BaseModel):
    """
        This represents the film information that is sent to the client

        Attributes:
            id (int): the id of the film
            title (str): the title of the film
            image_name (str): the name of the image of the film
            file_name (str): the name of the video of the film
    """
    id: int
    title: str
    image_name: str
    file_name: str