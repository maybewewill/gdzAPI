from pydantic import BaseModel



class Page(BaseModel):
    id: int
    number: str
    url: str