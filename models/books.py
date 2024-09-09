from pydantic import BaseModel
from .pages import Page
from typing import List, Optional


class Book(BaseModel):
    id: int
    name: str
    url: str
    authors: List[str]
    _pages: Optional[List[Page]] = None
    _gdz: Optional['GDZ'] = None

    @property
    def pages(self) -> List[Page]:
        if self._pages is None:
            if self._gdz is None:
                raise RuntimeError("GDZ instance not set for this Book")
            self._pages = self._gdz.get_pages(self.url)
        return self._pages

    class Config:
        arbitrary_types_allowed = True
