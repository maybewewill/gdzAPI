from pydantic import BaseModel
from typing import List, Optional
from .books import Book


class Subject(BaseModel):
    id: int
    name: str
    url: str
    _books: Optional[List[Book]] = None
    _gdz: Optional['GDZ'] = None


    @property
    def books(self) -> List[Book]:
        if self._books is None:
            if self._gdz is None:
                raise RuntimeError("GDZ instance not set for this Subject")
            self._books = self._gdz.get_books(self)
        return self._books

    class Config:
        arbitrary_types_allowed = True