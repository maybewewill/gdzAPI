import requests
from bs4 import BeautifulSoup as BS
from .models import *
from typing import List, Optional

class Euroki:

    _CLASS_SELECTOR = "#menuwka_new > ul.primary > li"
    _SUBJECT_SELECTOR = "body > div.bg_main > div.ads > div.ft_menu.clearfix > div:nth-child(2) > ul > li > a"
    _BOOK_SELECTOR = "body > div.bg_main > div.device_desktop.clearfix > div.dsk_main > div.content > ul > li > a"
    _PAGES_SELECTOR = "body > div > div.device_desktop.clearfix > div.dsk_main > div.content.one_page > div.txt_version > div > ul > li > a"
    _SOLUTION_SELECTOR = "#txt_cont > p > img"

    def __init__(self):
        self.BASE_URL = "https://euroki.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        }
        self.session = requests.Session()
        self.response = self.session.get(self.BASE_URL, headers=self.headers)
        self.soup = BS(self.response.text, 'lxml')
        self._subjects: Optional[List[Subject]] = None
        self._books: Optional[List[Book]] = None
        self._pages: Optional[List[Page]] = None
        self._solutions: Optional[List[Solution]] = None

    def _get(self,url):
        return BS(self.session.get(self.BASE_URL+url, headers=self.headers).text, "lxml")
    @property
    def classes(self):
        return [
            Class(
                id = id_,
                name = class_.select_one("a").text.strip(),
                url = f"/gdz/ru/vse/{12-id_}_klass",
                subjects=[
                    Subject(
                        id = id_,
                        name = subject.get("title"),
                        url = subject.get("href"),
                        _gdz = self
                    ) for id_, subject in enumerate(class_.select("ul > li.sbjcts > a")[:], 1)
                ]
            ) for id_, class_ in enumerate(self.soup.select(
                selector=self._CLASS_SELECTOR
            ),
            start=1)
        ]

    @property
    def subjects(self) -> List[Subject]:
        if self._subjects is None:
            self._subjects = self._get_subjects()
            for subject in self._subjects:
                subject._gdz = self
        return self._subjects

    def _get_subjects(self) -> List[Subject]:
        return [
            Subject(
                id=id_,
                name=subject.text.strip(),
                url=subject.get("href")
            ) for id_, subject in enumerate(self.soup.select(self._SUBJECT_SELECTOR), 1)
        ]

    def get_books(self, subject: Subject) -> List[Book]:
        self._books = None
        if self._books is None:
            self._books = self._get_books(subject)
            for book in self._books:
                book._gdz = self

        return self._books

    def _get_books(self, subject: Subject) -> List[Book]:
         return  [ Book(
                id = id_,
                name = book.select_one("div.rghpnl > div.bttl").text.strip(),
                url = book.get("href"),
                authors = book.select_one("div.rghpnl > div.book_description > div.book_mt > div > span").text.split(", "),
            ) for id_, book in enumerate(self._get(subject.url).select(
                selector=self._BOOK_SELECTOR
            ),
            start=1
            )]

    def get_pages(self, book: Book | str) -> List[Page]:
        self._pages = None
        if self._pages is None:
            self._pages = self._get_pages(book)
            for page in self._pages:
                page._gdz = self
        return self._pages

    def _get_pages(self, book: Book | str) -> List[Page]:
        return [
            Page(
                id = id_,
                url = page.get("href"),
                number = page.text.strip()
            ) for id_, page in enumerate(self._get(book.url if isinstance(book, Book) else book).select(
                selector=self._PAGES_SELECTOR
            ),
            start=1
            )]

    def get_gdz(self, page: Page | str) -> List[Solution]:
        self._solutions = None
        if self._solutions is None:
            self._solutions = self._get_gdz(page)
            for solution in self._solutions:
                solution._gdz = self
        return self._solutions

    def _get_gdz(self, page: Page | str) -> List[Solution]:
        return [
            Solution(
                id = id_,
                image_src = solution.get("src"),
                title = None
            ) for id_, solution in enumerate(self._get(
                page.url if isinstance(page, Page) else page
            ).select(
                selector=self._SOLUTION_SELECTOR)
            ,
            start=1
        )]

    def search_books(self, query: str) -> List[Book]:
        all_books = []
        for subject in self.subjects:
            all_books.extend(self.get_books(subject))

        return [book for book in all_books if query.lower() in book.name.lower()]

