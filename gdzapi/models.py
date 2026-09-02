"""Pydantic v2 data models for gdzapi."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Generic, Iterable, Iterator, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, PrivateAttr

T = TypeVar("T")


class AwaitableList(list, Generic[T]):
    """A list that also implements __await__, allowing it to be awaited multiple times."""

    def __await__(self) -> Iterator[Any]:
        async def _resolve() -> AwaitableList[T]:
            return self

        return _resolve().__await__()


class LazyAsyncList(Generic[T]):
    """Lazy loader for async properties that loads on first await and caches the result."""

    def __init__(
        self,
        fetch_fn: Callable[[], Awaitable[Iterable[T]]],
        on_complete: Callable[[AwaitableList[T]], None],
    ):
        self._fetch_fn = fetch_fn
        self._on_complete = on_complete

    def __await__(self) -> Iterator[Any]:
        async def _run() -> AwaitableList[T]:
            res = await self._fetch_fn()
            result_list = AwaitableList[T](res)
            self._on_complete(result_list)
            return result_list

        return _run().__await__()


class Solution(BaseModel):
    """Represents a solution, which can contain an image, text, or HTML."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    image_src: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None
    html: Optional[str] = None


class Page(BaseModel):
    """Represents a task, page, or exercise number in a book."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    number: str
    url: str

    _solutions: Optional[List[Solution]] = PrivateAttr(default=None)
    _client: Optional[Any] = PrivateAttr(default=None)

    def bind_client(self, client: Any) -> Page:
        self._client = client
        return self

    @property
    def solutions(self) -> Any:
        if self._solutions is not None:
            return self._solutions
        if self._client is None:
            raise RuntimeError("Client instance not bound for this Page")

        if getattr(self._client, "_is_async", False):
            def _set(val: AwaitableList[Solution]) -> None:
                self._solutions = val

            return LazyAsyncList(lambda: self._client.get_solutions(self.url), _set)

        self._solutions = self._client.get_solutions(self.url)
        return self._solutions

    async def get_solutions(self) -> List[Solution]:
        """Explicit async method to retrieve solutions."""
        if self._solutions is not None:
            return self._solutions
        if self._client is None:
            raise RuntimeError("Client instance not bound for this Page")
        res = await self._client.get_solutions(self.url)
        self._solutions = AwaitableList(res)
        return self._solutions


class Book(BaseModel):
    """Represents a textbook, workbook, or solution manual."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    name: str
    url: str
    authors: List[str] = []

    _pages: Optional[List[Page]] = PrivateAttr(default=None)
    _client: Optional[Any] = PrivateAttr(default=None)

    def bind_client(self, client: Any) -> Book:
        self._client = client
        return self

    @property
    def pages(self) -> Any:
        if self._pages is not None:
            return self._pages
        if self._client is None:
            raise RuntimeError("Client instance not bound for this Book")

        if getattr(self._client, "_is_async", False):
            def _set(val: AwaitableList[Page]) -> None:
                self._pages = val

            return LazyAsyncList(lambda: self._client.get_pages(self.url), _set)

        self._pages = self._client.get_pages(self.url)
        return self._pages

    async def get_pages(self) -> List[Page]:
        """Explicit async method to retrieve pages."""
        if self._pages is not None:
            return self._pages
        if self._client is None:
            raise RuntimeError("Client instance not bound for this Book")
        res = await self._client.get_pages(self.url)
        self._pages = AwaitableList(res)
        return self._pages


class Subject(BaseModel):
    """Represents a school subject (e.g. Mathematics, Biology)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    name: str
    url: str

    _books: Optional[List[Book]] = PrivateAttr(default=None)
    _client: Optional[Any] = PrivateAttr(default=None)

    def bind_client(self, client: Any) -> Subject:
        self._client = client
        return self

    @property
    def books(self) -> Any:
        if self._books is not None:
            return self._books
        if self._client is None:
            raise RuntimeError("Client instance not bound for this Subject")

        if getattr(self._client, "_is_async", False):
            def _set(val: AwaitableList[Book]) -> None:
                self._books = val

            return LazyAsyncList(lambda: self._client.get_books(self), _set)

        self._books = self._client.get_books(self)
        return self._books

    async def get_books(self) -> List[Book]:
        """Explicit async method to retrieve books."""
        if self._books is not None:
            return self._books
        if self._client is None:
            raise RuntimeError("Client instance not bound for this Subject")
        res = await self._client.get_books(self)
        self._books = AwaitableList(res)
        return self._books


class Class(BaseModel):
    """Represents a school grade/class."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    name: str
    url: str = ""
    subjects: List[Subject] = []


__all__ = [
    "Class",
    "Subject",
    "Book",
    "Page",
    "Solution",
    "AwaitableList",
    "LazyAsyncList",
]
