from pydantic import BaseModel
from .subjects import Subject

class Class(BaseModel):
    name: str
    id: int
    url: str
    subjects: list[Subject]

