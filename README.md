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
$ pip install gdzapi --upgrade
```
-----
## Usage
### Synchronous Usage
Here's a basic example of how to use the synchronous GDZ class:

```python

from gdzapi.gdzapi import GDZ

gdz = GDZ()

for subject in gdz.subjects:
    if subject.name == "Биология":
        book = gdz.get_books(subject)[0]
        print(f"Book: {book.name}")

        pages = gdz.get_pages(book.url)
        print(f"Number of pages: {len(pages)}")

        if pages:
            solutions = gdz.get_gdz(pages[0].url)
            print(f"Number of solutions: {len(solutions)}")
```
-----
### Asynchronous Usage
Here's how to use the asynchronous AsyncGDZ class:

```python
import asyncio
from gdzapi.gdzapi import AsyncGDZ


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
                    print(f"Number of solutions: {len(solutions)}")


if __name__ == "__main__":
    asyncio.run(main())
```
-----
## API Reference


### GDZ Class

classes: List of available classes

subjects: List of available subjects

get_books(subject: Subject) -> List[Book]: Get books for a subject

get_pages(url: str) -> List[Page]: Get pages for a given URL

get_gdz(url: str) -> List[Solution]: Get solutions for a given URL

-----
### AsyncGDZ Class

classes: Asynchronous property returning list of available classes

subjects: Asynchronous property returning list of available subjects

get_books(subject: Subject) -> List[Book]: Asynchronous method to get books for a subject

get_pages(url: str) -> List[Page]: Asynchronous method to get pages for a given URL

get_gdz(url: str) -> List[Solution]: Asynchronous method to get solutions for a given URL

-----

## License

`gdzAPI` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.