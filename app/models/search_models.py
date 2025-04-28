from typing import List
from pydantic import BaseModel

class SearchResponseModel(BaseModel):
    results: List[int]
    token: str