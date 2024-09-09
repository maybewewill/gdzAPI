from pydantic import BaseModel
from typing import List, Optional
from .solutions import Solution

class Page(BaseModel):
    id: int
    number: str
    url: str

    _solutions: Optional[List[Solution]] = None
    _gdz: Optional['GDZ'] = None

    @property
    def solutions(self) -> List[Solution]:
        if self._solutions is None:
            if self._gdz is None:
                raise RuntimeError("GDZ instance not set for this Subject")
            self._solutions = self._gdz.get_gdz(self.url)
        return self._solutions

    class Config:
        arbitrary_types_allowed = True