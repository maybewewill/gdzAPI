# gdz API
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/downloads/release/python-391/)
[![PyPI - Version](https://img.shields.io/pypi/v/gdzapi.svg)](https://pypi.org/project/gdzapi)
-----
**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [API Reference](#api-reference)
-----
An asynchronous Python library for accessing GDZ (Готовые домашние задания) resources.

-----
## Installation
### Stable version
```bash
pip install gdzapi --upgrade
```
-----
## Usage
### Synchronous Usage
Here's a basic example of how to use the synchronous GDZ class:

```python
# First type of usage
from gdzapi import GDZ

gdz = GDZ()

for subject in gdz.subjects:
    if subject.name == "Биология":
        book = gdz.get_books(subject)[0]
        print(f"Book: {book.name}")

        pages = gdz.get_pages(book.url)
        print(f"Number of pages: {len(pages)}")

        if pages:
            solutions = gdz.get_gdz(pages[0].url)
            image_url = solutions[0].image_src
            print(image_url)

#--------------------------------------------------------------
            
# Second type of usage
from gdzapi import GDZ

gdz = GDZ()

subjects = gdz.subjects
for subject in subjects:
    if subject.name == "Биология":
        book = subject.books[0]
        print(f"Book: {book.name}")
        
        page = book.pages[0]
        
        if page:
            solutions = page.solutions
            image_url = solutions[0].image_src
            print(image_url)
```
-----
### Asynchronous Usage
Here's how to use the asynchronous AsyncGDZ class:

```python
# First type of usage
import asyncio
from gdzapi import AsyncGDZ

async def main():
    async with AsyncGDZ() as gdz:
        subjects = await gdz.subjects
        for subject in subjects:
            if subject.name == "Биология":
                books = await gdz.get_books(subject)
                if books:
                    book = books[0]
                    print(f"Book: {book.name}")

                pages = await gdz.get_pages(book.url)
                print(f"Number of pages: {len(pages)}")

                if pages:
                    solutions = await gdz.get_gdz(pages[0].url)
                    print(solutions[0].image_src)

if __name__ == "__main__":
    asyncio.run(main())

#--------------------------------------------------------------
    
# Second type of usage
import asyncio
from gdzapi import AsyncGDZ

async def main():
    async with AsyncGDZ() as gdz:
        subjects = await gdz.subjects
        for subject in subjects:
            if subject.name == "Биология":
                books = await subject.books
                if books:
                    book = books[0]
                    print(f"Book: {book.name}")
                
                pages = await book.pages
                if pages:
                    solutions = await pages[0].solutions
                    print(solutions[0].image_src)

if __name__ == "__main__":
    asyncio.run(main())
```
## Euroki example
```python

from gdzapi import Euroki

e = Euroki()
books = e.search_books("Биология 10 класс")
for book in books:
    if "Каменский" in book.authors:
        downloadable_images = []
        for i in book.pages:
            for j in i.solutions:
                downloadable_images.append(j.image_src)
        print(downloadable_images)
```
## MegaResheba example
```python
from gdzapi import MegaResheba

m = MegaResheba()
for s in m.subjects:
    if s.name == "История":
        try:
            print(s.books[0].pages[0].solutions[0].image_src)
        except:
            # This is means that there are no solutions
            print("No solutions")
```

-----
## API Reference


### GDZ/Euroki/MegaResheba Class

``classes``: List of available classes

``subjects``: List of available subjects

``get_books(subject: Subject) -> List[Book]:`` Get books for a subject

``get_pages(url: str) -> List[Page]:`` Get pages for a given URL

``get_gdz(url: str) -> List[Solution]:`` Get solutions for a given URL

``search_books(query: str) -> List[Book]:`` Search books for a given query

-----
### AsyncGDZ Class

``classes``: Asynchronous property returning list of available classes

``subjects``: Asynchronous property returning list of available subjects

``get_books(subject: Subject) -> List[Book]:`` Asynchronous method to get books for a subject

``get_pages(url: str) -> List[Page]:`` Asynchronous method to get pages for a given URL

``get_gdz(url: str) -> List[Solution]:`` Asynchronous method to get solutions for a given URL

``search_books(query: str) -> List[Book]:`` Asynchronous method to search books for a given query

## License

`gdzAPI` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.