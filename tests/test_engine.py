"""Unit tests for unified Client and AsyncClient engine."""

from __future__ import annotations

from unittest.mock import MagicMock
from bs4 import BeautifulSoup as BS
import pytest

from gdzapi.client import AsyncClient, Client
from gdzapi.models import Book, Page, Solution, Subject
from gdzapi.providers import ProviderSpec


@pytest.fixture
def mock_spec() -> ProviderSpec:
    return ProviderSpec(
        name="mock",
        base_url="https://example.com",
        display_name="Mock",
        extract_classes=lambda soup, base, client: [],
        extract_subjects=lambda soup, base, client: [
            Subject(id=1, name="Алгебра", url="/algebra").bind_client(client),
            Subject(id=2, name="Физика", url="/physics").bind_client(client),
        ],
        extract_books=lambda soup, base, client: [
            Book(id=1, name="Алгебра 10 класс", url="/book1").bind_client(client)
        ],
        extract_pages=lambda soup, base, client: [
            Page(id=1, number="10", url="/task1").bind_client(client)
        ],
        extract_solutions=lambda soup, base, client: [
            Solution(id=1, image_src="https://example.com/img.png")
        ],
    )


def test_client_sync_engine(mock_spec):
    client = Client(provider=mock_spec)
    client.http.get = MagicMock(return_value=BS("<html></html>", "html.parser"))

    subjects = client.subjects
    assert len(subjects) == 2
    # test caching
    assert client.subjects is subjects

    books = client.get_books(subjects[0])
    assert len(books) == 1
    assert books[0].name == "Алгебра 10 класс"

    # Search books
    results = client.search_books("Алгебра")
    assert len(results) >= 1

    # Context manager
    with client as c:
        assert c is client


@pytest.mark.asyncio
async def test_client_async_engine(mock_spec):
    async with AsyncClient(provider=mock_spec) as client:
        async def mock_get(url: str):
            return BS("<html></html>", "html.parser")

        client.http.get = mock_get

        subjects = await client.get_subjects()
        assert len(subjects) == 2

        books = await client.get_books(subjects[0])
        assert len(books) == 1

        pages = await client.get_pages(books[0])
        assert len(pages) == 1

        solutions = await client.get_solutions(pages[0])
        assert len(solutions) == 1
        assert solutions[0].image_src == "https://example.com/img.png"
