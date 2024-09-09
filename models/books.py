from pydantic import BaseModel

from typing import List


class Book(BaseModel):
    id: int
    name: str
    url: str
    authors: List[str]
    years: str