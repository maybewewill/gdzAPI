import requests
from bs4 import BeautifulSoup as BS
from .models import *
from typing import List, Optional

class MegaResheba:

    _CLASS_SELECTOR = "body > div > div > main > div.mainMenu.desktopMenu > ul > li"
    _SUBJECT_SELECTOR = "body > div > div > main > div.content > ul.indexTable > li > div > a"
    _BOOK_SELECTOR = "body > div > div > main > div.content > ul > li > a.book"
    _PAGES_SELECTOR = "#tasks > div > div > a"
    _SOLUTION_SELECTOR = "#task > div > div > img"
    def __init__(self):
        self.BASE_URL = "https://megaresheba.ru"
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
                url = f"/publ/reshebnik/{id_}_klass/118-1-0-{1431+id_}",
                subjects=[
                    Subject(
                        id = id_,
                        name = subject.text.strip(),
                        url = subject.get("href"),
                        gdz = self
                    ) for id_, subject in enumerate(class_.select("a")[1:], 1)
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
                name = ' '.join(book.select_one("div.bookDescription > div.bigText.bolder").text.split()),
                url = book.get("href"),
                authors = [x.text for x in book.select("div.m5 > span")[:-1]],
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
                number = page.select_one("span").text
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


