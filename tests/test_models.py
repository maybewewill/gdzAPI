"""Unit tests for models and lazy navigation."""

from __future__ import annotations

import asyncio
import pytest
from gdzapi.models import AwaitableList, Book, Class, Page, Solution, Subject


class FakeSyncClient:
    def __init__(self):
        self._is_async = False
        self.books_call_count = 0
        self.pages_call_count = 0
        self.solutions_call_count = 0

    def get_books(self, subject: Subject) -> list[Book]:
        self.books_call_count += 1
        return [Book(id=1, name="Математика 1", url="/math-1", authors=["Автор А"])]

    def get_pages(self, url: str) -> list[Page]:
        self.pages_call_count += 1
        return [Page(id=1, number="1", url="/math-1/p1")]

    def get_solutions(self, url: str) -> list[Solution]:
        self.solutions_call_count += 1
        return [Solution(id=1, image_src="https://example.com/1.jpg", title="Решение 1")]


class FakeAsyncClient:
    def __init__(self):
        self._is_async = True
        self.books_call_count = 0
        self.pages_call_count = 0
        self.solutions_call_count = 0

    async def get_books(self, subject: Subject) -> list[Book]:
        self.books_call_count += 1
        await asyncio.sleep(0.001)
        return [Book(id=1, name="Математика 1", url="/math-1", authors=["Автор А"])]

    async def get_pages(self, url: str) -> list[Page]:
        self.pages_call_count += 1
        await asyncio.sleep(0.001)
        return [Page(id=1, number="1", url="/math-1/p1")]

    async def get_solutions(self, url: str) -> list[Solution]:
        self.solutions_call_count += 1
        await asyncio.sleep(0.001)
        return [Solution(id=1, image_src="https://example.com/1.jpg", title="Решение 1")]


def test_models_instantiation():
    sol = Solution(id=1, image_src="https://test.com/img.jpg", title="Title", text="Ответ 1")
    assert sol.id == 1
    assert sol.image_src == "https://test.com/img.jpg"
    assert sol.title == "Title"
    assert sol.text == "Ответ 1"

    p = Page(id=1, number="5", url="/page-5")
    assert p.number == "5"

    b = Book(id=1, name="Book A", url="/b-a", authors=["X", "Y"])
    assert b.authors == ["X", "Y"]

    s = Subject(id=1, name="Математика", url="/math")
    assert s.name == "Математика"

    c = Class(id=1, name="1 класс", url="/c-1", subjects=[s])
    assert len(c.subjects) == 1


def test_unbound_client_raises():
    s = Subject(id=1, name="Test", url="/test")
    with pytest.raises(RuntimeError, match="Client instance not bound"):
        _ = s.books

    b = Book(id=1, name="Test", url="/test")
    with pytest.raises(RuntimeError, match="Client instance not bound"):
        _ = b.pages

    p = Page(id=1, number="1", url="/test")
    with pytest.raises(RuntimeError, match="Client instance not bound"):
        _ = p.solutions


def test_sync_lazy_navigation_caches():
    client = FakeSyncClient()
    s = Subject(id=1, name="Математика", url="/math").bind_client(client)

    # First access fetches
    books1 = s.books
    assert len(books1) == 1
    assert books1[0].name == "Математика 1"
    assert client.books_call_count == 1

    # Second access uses cache
    books2 = s.books
    assert books1 == books2
    assert client.books_call_count == 1

    # Chain to page
    book = books1[0].bind_client(client)
    pages1 = book.pages
    assert len(pages1) == 1
    assert client.pages_call_count == 1
    _ = book.pages
    assert client.pages_call_count == 1

    # Chain to solution
    page = pages1[0].bind_client(client)
    sols1 = page.solutions
    assert len(sols1) == 1
    assert client.solutions_call_count == 1
    _ = page.solutions
    assert client.solutions_call_count == 1


@pytest.mark.asyncio
async def test_async_lazy_navigation_and_multiple_awaits():
    client = FakeAsyncClient()
    s = Subject(id=1, name="Математика", url="/math").bind_client(client)

    # First await executes
    books1 = await s.books
    assert len(books1) == 1
    assert books1[0].name == "Математика 1"
    assert client.books_call_count == 1

    # Second await must NOT crash with "cannot reuse already awaited coroutine"
    books2 = await s.books
    assert books1 == books2
    assert client.books_call_count == 1

    # Can index and iterate directly
    assert books2[0].name == "Математика 1"
    assert len(books2) == 1

    # Book pages
    book = books1[0].bind_client(client)
    pages1 = await book.pages
    assert len(pages1) == 1
    assert client.pages_call_count == 1
    pages2 = await book.pages
    assert pages1 == pages2
    assert client.pages_call_count == 1

    # Page solutions
    page = pages1[0].bind_client(client)
    sols1 = await page.solutions
    assert len(sols1) == 1
    assert client.solutions_call_count == 1
    sols2 = await page.solutions
    assert sols1 == sols2
    assert client.solutions_call_count == 1


@pytest.mark.asyncio
async def test_explicit_async_methods():
    client = FakeAsyncClient()
    s = Subject(id=1, name="Математика", url="/math").bind_client(client)
    books = await s.get_books()
    assert len(books) == 1

    book = books[0].bind_client(client)
    pages = await book.get_pages()
    assert len(pages) == 1

    page = pages[0].bind_client(client)
    sols = await page.get_solutions()
    assert len(sols) == 1
