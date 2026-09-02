"""Unified synchronous and asynchronous client engine for gdzapi."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote_plus
from bs4 import BeautifulSoup as BS
import requests

from .exceptions import NetworkError, ParsingError
from .models import AwaitableList, Book, Class, LazyAsyncList, Page, Solution, Subject
from .providers import Provider, ProviderSpec, get_provider_spec
from .utils import DEFAULT_HEADERS, DEFAULT_TIMEOUT, normalize_url

try:
    import aiohttp
except ImportError:
    aiohttp = None  # type: ignore


def parse_soup(content: Union[str, bytes], parser: str = "lxml") -> BS:
    """Safely parse HTML into BeautifulSoup, falling back to html.parser if lxml fails."""
    try:
        return BS(content, parser)
    except Exception:
        return BS(content, "html.parser")


# ---------------------------------------------------------------------------
# HTTP Session Wrappers
# ---------------------------------------------------------------------------

class SyncHTTPClient:
    """Synchronous HTTP client using requests."""

    def __init__(
        self,
        base_url: str,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        merged_headers = dict(DEFAULT_HEADERS)
        if headers:
            merged_headers.update(headers)
        self.session = requests.Session()
        self.session.headers.update(merged_headers)

    def get(self, path_or_url: str, **kwargs: Any) -> BS:
        url = normalize_url(self.base_url, path_or_url)
        timeout = kwargs.pop("timeout", self.timeout)
        try:
            resp = self.session.get(url, timeout=timeout, **kwargs)
            resp.raise_for_status()
            return parse_soup(resp.content)
        except requests.RequestException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            raise NetworkError(f"HTTP request failed: {e}", url=url, status_code=status) from e

    def close(self) -> None:
        self.session.close()


class AsyncHTTPClient:
    """Asynchronous HTTP client using aiohttp."""

    def __init__(
        self,
        base_url: str,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
    ):
        if aiohttp is None:
            raise RuntimeError("aiohttp is required for async clients. Install it with: pip install aiohttp")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        merged_headers = dict(DEFAULT_HEADERS)
        if headers:
            merged_headers.update(headers)
        self.headers = merged_headers
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout_cfg = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(headers=self.headers, timeout=timeout_cfg)
        return self._session

    async def get(self, path_or_url: str, **kwargs: Any) -> BS:
        url = normalize_url(self.base_url, path_or_url)
        session = await self._get_session()
        try:
            async with session.get(url, **kwargs) as resp:
                if resp.status >= 400:
                    raise NetworkError(f"HTTP error {resp.status}", url=url, status_code=resp.status)
                content = await resp.read()
                return parse_soup(content)
        except aiohttp.ClientError as e:
            raise NetworkError(f"Async HTTP request failed: {e}", url=url) from e
        except asyncio.TimeoutError as e:
            raise NetworkError(f"Async HTTP request timed out after {self.timeout}s", url=url) from e

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()


# ---------------------------------------------------------------------------
# Unified Synchronous Client
# ---------------------------------------------------------------------------

class Client:
    """Unified synchronous client for all supported GDZ providers."""

    def __init__(
        self,
        provider: Union[str, ProviderSpec] = Provider.GDZ,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.spec = get_provider_spec(provider)
        self.base_url = self.spec.base_url
        merged_headers = dict(self.spec.headers or {})
        if headers:
            merged_headers.update(headers)
        self.http = SyncHTTPClient(self.base_url, timeout=timeout, headers=merged_headers)
        self._is_async = False
        self._cached_classes: Optional[List[Class]] = None
        self._cached_subjects: Optional[List[Subject]] = None

    # Factory methods
    @classmethod
    def gdz(cls, **kwargs: Any) -> Client:
        return cls(Provider.GDZ, **kwargs)

    @classmethod
    def euroki(cls, **kwargs: Any) -> Client:
        return cls(Provider.EUROKI, **kwargs)

    @classmethod
    def megaresheba(cls, **kwargs: Any) -> Client:
        return cls(Provider.MEGARESHEBA, **kwargs)

    @classmethod
    def raketa(cls, **kwargs: Any) -> Client:
        return cls(Provider.RAKETA, **kwargs)

    @classmethod
    def skysmart(cls, **kwargs: Any) -> Client:
        return cls(Provider.SKYSMART, **kwargs)

    @classmethod
    def reshak(cls, **kwargs: Any) -> Client:
        return cls(Provider.RESHAK, **kwargs)

    @classmethod
    def pomogalka(cls, **kwargs: Any) -> Client:
        return cls(Provider.POMOGALKA, **kwargs)

    @classmethod
    def putina(cls, **kwargs: Any) -> Client:
        return cls(Provider.PUTINA, **kwargs)

    @classmethod
    def ltd(cls, **kwargs: Any) -> Client:
        return cls(Provider.LTD, **kwargs)

    def get_classes(self) -> List[Class]:
        if self.spec.extract_classes is None:
            return []
        soup = self.http.get(self.spec.classes_url)
        classes = self.spec.extract_classes(soup, self.base_url, self)
        self._cached_classes = classes
        return classes

    @property
    def classes(self) -> List[Class]:
        if self._cached_classes is None:
            self._cached_classes = self.get_classes()
        return self._cached_classes

    def get_subjects(self) -> List[Subject]:
        if self.spec.extract_subjects is None:
            return []
        soup = self.http.get(self.spec.subjects_url)
        subjects = self.spec.extract_subjects(soup, self.base_url, self)
        self._cached_subjects = subjects
        return subjects

    @property
    def subjects(self) -> List[Subject]:
        if self._cached_subjects is None:
            self._cached_subjects = self.get_subjects()
        return self._cached_subjects

    def get_books(self, subject: Union[Subject, str]) -> List[Book]:
        if self.spec.extract_books is None:
            return []
        url = subject.url if isinstance(subject, Subject) else subject
        soup = self.http.get(url)
        return self.spec.extract_books(soup, self.base_url, self)

    def get_pages(self, book: Union[Book, str]) -> List[Page]:
        if self.spec.extract_pages is None:
            return []
        url = book.url if isinstance(book, Book) else book
        soup = self.http.get(url)
        return self.spec.extract_pages(soup, self.base_url, self)

    def get_solutions(self, page: Union[Page, str]) -> List[Solution]:
        url = page.url if isinstance(page, Page) else page
        if url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return [Solution(id=1, image_src=normalize_url(self.base_url, url), title="Решение")]
        if self.spec.extract_solutions is None:
            return []
        soup = self.http.get(url)
        return self.spec.extract_solutions(soup, self.base_url, self)

    def search_books(self, query: str, subject: Optional[Union[Subject, str]] = None) -> List[Book]:
        """Search books by name or query string."""
        if self.spec.search_path_template and self.spec.extract_search_books:
            search_path = self.spec.search_path_template.format(query=quote_plus(query))
            soup = self.http.get(search_path)
            return self.spec.extract_search_books(soup, self.base_url, self)

        # Fallback to subject filtering
        query_lower = query.lower()
        results: List[Book] = []

        if subject is not None:
            target_subjects = [subject if isinstance(subject, Subject) else Subject(id=0, name="Target", url=subject)]
        else:
            target_subjects = self.subjects

        for s in target_subjects:
            try:
                for b in self.get_books(s):
                    if query_lower in b.name.lower():
                        results.append(b)
            except Exception:
                continue

        return results

    def close(self) -> None:
        self.http.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Unified Asynchronous Client
# ---------------------------------------------------------------------------

class AsyncClient:
    """Unified asynchronous client for all supported GDZ providers."""

    def __init__(
        self,
        provider: Union[str, ProviderSpec] = Provider.GDZ,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.spec = get_provider_spec(provider)
        self.base_url = self.spec.base_url
        merged_headers = dict(self.spec.headers or {})
        if headers:
            merged_headers.update(headers)
        self.http = AsyncHTTPClient(self.base_url, timeout=timeout, headers=merged_headers)
        self._is_async = True
        self._cached_classes: Optional[AwaitableList[Class]] = None
        self._cached_subjects: Optional[AwaitableList[Subject]] = None

    # Factory methods
    @classmethod
    def gdz(cls, **kwargs: Any) -> AsyncClient:
        return cls(Provider.GDZ, **kwargs)

    @classmethod
    def euroki(cls, **kwargs: Any) -> AsyncClient:
        return cls(Provider.EUROKI, **kwargs)

    @classmethod
    def megaresheba(cls, **kwargs: Any) -> AsyncClient:
        return cls(Provider.MEGARESHEBA, **kwargs)

    @classmethod
    def raketa(cls, **kwargs: Any) -> AsyncClient:
        return cls(Provider.RAKETA, **kwargs)

    @classmethod
    def skysmart(cls, **kwargs: Any) -> AsyncClient:
        return cls(Provider.SKYSMART, **kwargs)

    @classmethod
    def reshak(cls, **kwargs: Any) -> AsyncClient:
        return cls(Provider.RESHAK, **kwargs)

    @classmethod
    def pomogalka(cls, **kwargs: Any) -> AsyncClient:
        return cls(Provider.POMOGALKA, **kwargs)

    @classmethod
    def putina(cls, **kwargs: Any) -> AsyncClient:
        return cls(Provider.PUTINA, **kwargs)

    @classmethod
    def ltd(cls, **kwargs: Any) -> AsyncClient:
        return cls(Provider.LTD, **kwargs)

    async def get_classes(self) -> List[Class]:
        if self.spec.extract_classes is None:
            return []
        soup = await self.http.get(self.spec.classes_url)
        classes = self.spec.extract_classes(soup, self.base_url, self)
        self._cached_classes = AwaitableList(classes)
        return self._cached_classes

    @property
    def classes(self) -> Any:
        if self._cached_classes is not None:
            return self._cached_classes

        def _set(val: AwaitableList[Class]) -> None:
            self._cached_classes = val

        return LazyAsyncList(self.get_classes, _set)

    async def get_subjects(self) -> List[Subject]:
        if self.spec.extract_subjects is None:
            return []
        soup = await self.http.get(self.spec.subjects_url)
        subjects = self.spec.extract_subjects(soup, self.base_url, self)
        self._cached_subjects = AwaitableList(subjects)
        return self._cached_subjects

    @property
    def subjects(self) -> Any:
        if self._cached_subjects is not None:
            return self._cached_subjects

        def _set(val: AwaitableList[Subject]) -> None:
            self._cached_subjects = val

        return LazyAsyncList(self.get_subjects, _set)

    async def get_books(self, subject: Union[Subject, str]) -> List[Book]:
        if self.spec.extract_books is None:
            return []
        url = subject.url if isinstance(subject, Subject) else subject
        soup = await self.http.get(url)
        return self.spec.extract_books(soup, self.base_url, self)

    async def get_pages(self, book: Union[Book, str]) -> List[Page]:
        if self.spec.extract_pages is None:
            return []
        url = book.url if isinstance(book, Book) else book
        soup = await self.http.get(url)
        return self.spec.extract_pages(soup, self.base_url, self)

    async def get_solutions(self, page: Union[Page, str]) -> List[Solution]:
        url = page.url if isinstance(page, Page) else page
        if url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return [Solution(id=1, image_src=normalize_url(self.base_url, url), title="Решение")]
        if self.spec.extract_solutions is None:
            return []
        soup = await self.http.get(url)
        return self.spec.extract_solutions(soup, self.base_url, self)

    async def search_books(self, query: str, subject: Optional[Union[Subject, str]] = None) -> List[Book]:
        """Search books asynchronously by query string."""
        if self.spec.search_path_template and self.spec.extract_search_books:
            search_path = self.spec.search_path_template.format(query=quote_plus(query))
            soup = await self.http.get(search_path)
            return self.spec.extract_search_books(soup, self.base_url, self)

        # Fallback to concurrent subject filtering
        query_lower = query.lower()

        if subject is not None:
            target_subjects = [subject if isinstance(subject, Subject) else Subject(id=0, name="Target", url=subject)]
        else:
            target_subjects = await self.get_subjects()

        async def _fetch_and_filter(s: Subject) -> List[Book]:
            try:
                books = await self.get_books(s)
                return [b for b in books if query_lower in b.name.lower()]
            except Exception:
                return []

        nested = await asyncio.gather(*[_fetch_and_filter(s) for s in target_subjects])
        results: List[Book] = []
        for sublist in nested:
            results.extend(sublist)
        return results

    async def close(self) -> None:
        await self.http.close()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
