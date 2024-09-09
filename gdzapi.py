import requests
from bs4 import BeautifulSoup as BS
from .models import *
from typing import List
import aiohttp
import logging

class GDZ:

    CLASSES_SELECTOR = "body > div > div.page > aside > div.sidebar__main > div > ul > li"
    SUBJECTS_SELECTOR = "body > div.layout > div.page > main > table > tbody > tr > td.table-section-heading > a"
    BOOKS_SELECTOR = "body > div > div.page > main > ul.book__list > li > a"
    PAGES_SELECTOR = "body > div > div.page > main > div.task__list.js-tasks-container"
    GDZ_SELECTOR = "body > div.layout > div.page > main > figure > div.task-img-container > div > img"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.BASE_URL = "https://www.gdz.ru"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        }
        self.session = requests.Session()
        self.response = self.session.get(self.BASE_URL, headers=self.headers)
        self.soup = BS(self.response.text, 'lxml')

    def get(self, url: str) -> BS | None:
        try:
            response = self.session.get(self.BASE_URL + url, headers=self.headers)
            response.raise_for_status()
            return BS(response.text, "lxml")
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return

    @property
    def get_html(self) -> str:
        return self.response.text

    @property
    def classes(self) -> List[Class]:
        return [
            Class(
                id = id_,
                name = class_.select_one("a").text.strip(),
                url = f"/class-{id_}",
                subjects=[
                    Subject(
                        id = id_,
                        name = subject.text.strip(),
                        url = subject.get("href")
                    ) for id_, subject in enumerate(class_.select(selector="ul > li > a")[1:], 1)
                ]
            ) for id_, class_ in enumerate(self.soup.select(
                    selector=self.CLASSES_SELECTOR
                ),
                start=1
            )
        ]

    @property
    def subjects(self) -> List[Subject]:
        return [
            Subject(
                id = id_,
                name = subject.text.strip(),
                url = subject.get("href")
            )
            for id_, subject in enumerate(
                self.soup.select(
                    selector=self.SUBJECTS_SELECTOR
                ),
                start=1)
        ]

    def get_books(self, subject: Subject) -> List[Book]:
        return [
            Book(
                id = id_,
                name = book.get("title"),
                url = book.get("href"),
                authors = book.select("div > p > span")[0].text.split(", "),
                years = book.select("div > p")[-1].text.strip(),

            )
            for id_, book in enumerate(
                self.get(subject.url).select(
                    selector=self.BOOKS_SELECTOR
                ),
                start=1)
        ]


    def get_pages(self, url: str) -> List[Page]:
        return [
            Page(
                id = id_,
                number = page.text.strip(),
                url = page.get("href")
            )
            for id_, page in enumerate(
                self.get(url).select_one(
                    selector=self.PAGES_SELECTOR
                    ).select(
                        selector="div > a"
                    ),
                start=1)
        ]

    def get_gdz(self, url: str) -> List[Solution]:
        return [
            Solution(
                id = id_,
                title = solution.get("alt").split("  ")[-1].strip(),
                image_src = solution.get("src")
            )
            for id_, solution in enumerate(
                self.get(url).select(
                    selector=self.GDZ_SELECTOR
                ),
                start=1)
        ]

class AsyncGDZ:

    CLASSES_SELECTOR = "body > div > div.page > aside > div.sidebar__main > div > ul > li"
    SUBJECTS_SELECTOR = "body > div.layout > div.page > main > table > tbody > tr > td.table-section-heading > a"
    BOOKS_SELECTOR = "body > div > div.page > main > ul.book__list > li > a"
    PAGES_SELECTOR = "body > div > div.page > main > div.task__list.js-tasks-container"
    GDZ_SELECTOR = "body > div.layout > div.page > main > figure > div.task-img-container > div > img"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.BASE_URL = "https://www.gdz.ru"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        }
        self.session = None
        self.soup = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def get(self, url: str) -> BS | None:
        try:
            async with self.session.get(self.BASE_URL + url, headers=self.headers) as response:
                response.raise_for_status()
                text = await response.text()
                return BS(text, "lxml")
        except aiohttp.ClientError as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None

    async def initialize(self):
        self.soup = await self.get("")

    @property
    async def classes(self) -> List[Class]:
        if not self.soup:
            await self.initialize()
        return [
            Class(
                id=id_,
                name=class_.select_one("a").text.strip(),
                url=f"/class-{id_}",
                subjects=[
                    Subject(
                        id=id_,
                        name=subject.text.strip(),
                        url=subject.get("href")
                    ) for id_, subject in enumerate(class_.select(selector="ul > li > a")[1:], 1)
                ]
            ) for id_, class_ in enumerate(self.soup.select(selector=self.CLASSES_SELECTOR), start=1)
        ]

    @property
    async def subjects(self) -> List[Subject]:
        if not self.soup:
            await self.initialize()
        return [
            Subject(
                id=id_,
                name=subject.text.strip(),
                url=subject.get("href")
            )
            for id_, subject in enumerate(
                self.soup.select(selector=self.SUBJECTS_SELECTOR),
                start=1)
        ]

    async def get_books(self, subject: Subject) -> List[Book]:
        soup = await self.get(subject.url)
        if not soup:
            return []
        return [
            Book(
                id=id_,
                name=book.get("title"),
                url=book.get("href"),
                authors=book.select("div > p > span")[0].text.split(", "),
                years=book.select("div > p")[-1].text.strip(),
            )
            for id_, book in enumerate(
                soup.select(selector=self.BOOKS_SELECTOR),
                start=1)
        ]

    async def get_pages(self, url: str) -> List[Page]:
        soup = await self.get(url)
        if not soup:
            return []
        pages_container = soup.select_one(selector=self.PAGES_SELECTOR)
        if not pages_container:
            return []
        return [
            Page(
                id=id_,
                number=page.text.strip(),
                url=page.get("href")
            )
            for id_, page in enumerate(
                pages_container.select(selector="div > a"),
                start=1)
        ]

    async def get_gdz(self, url: str) -> List[Solution]:
        soup = await self.get(url)
        if not soup:
            return []
        return [
            Solution(
                id=id_,
                title=solution.get("alt").split("  ")[-1].strip(),
                image_src=solution.get("src")
            )
            for id_, solution in enumerate(
                soup.select(selector=self.GDZ_SELECTOR),
                start=1)
        ]