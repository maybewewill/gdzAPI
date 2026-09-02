<div align="center">

  <h1>gdzapi</h1>
  <p>Universal asynchronous and synchronous Python client for 9 GDZ providers with declarative engine and Pydantic v2 validation.</p>

  <p>
    <a href="https://pypi.org/project/gdzapi"><img src="https://img.shields.io/pypi/v/gdzapi.svg?color=blue" alt="PyPI version" /></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="Python Versions" /></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT" /></a>
    <a href="https://github.com/maybewewill/gdzAPI"><img src="https://img.shields.io/badge/tests-33%20passed-success" alt="Tests" /></a>
  </p>

  <p>
    <a href="#quick-start">Quick Start</a> &middot;
    <a href="#supported-providers">9 Providers</a> &middot;
    <a href="#features">Features</a> &middot;
    <a href="#usage">Usage Guide</a> &middot;
    <a href="#architecture">Architecture</a> &middot;
    <a href="#license">License</a>
  </p>

</div>

---

## Why gdzapi

Most school scraping tools are fragmented across dozens of fragile files, lack asynchronous capability, crash on repeated awaits, or fail to handle modern SPA/lazy-loading structures.

**gdzapi** unifies **9 major school solution portals** under a single, declarative architecture. Instead of maintaining separate scrapers for each website, all providers are driven by a single engine with non-blocking initialization, strict timeouts, protocol normalization, and Pydantic v2 models.

---

## Supported Providers

| Provider | Alias | Sync Method | Async Method | Content Type | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GDZ.ru** | `"gdz"` | `Client.gdz()` | `AsyncClient.gdz()` | Images | Stable |
| **Euroki.org** | `"euroki"` | `Client.euroki()` | `AsyncClient.euroki()` | Images (lazy) | Stable |
| **MegaResheba.ru** | `"megaresheba"` | `Client.megaresheba()` | `AsyncClient.megaresheba()` | Images | Stable |
| **GDZ-Raketa.ru** | `"raketa"` | `Client.raketa()` | `AsyncClient.raketa()` | Text, MathJax & Images | Stable |
| **Reshak.ru** | `"reshak"` | `Client.reshak()` | `AsyncClient.reshak()` | Images | Stable |
| **Pomogalka.me** | `"pomogalka"` | `Client.pomogalka()` | `AsyncClient.pomogalka()` | Images | Stable |
| **Resh.Skysmart.ru** | `"skysmart"` | `Client.skysmart()` | `AsyncClient.skysmart()` | Steps & Images | Stable (SSR) |
| **GDZ-Putina.fun** | `"putina"` | `Client.putina()` | `AsyncClient.putina()` | High-res Images (JSON) | Stable |
| **GDZ.ltd** | `"ltd"` | `Client.ltd()` | `AsyncClient.ltd()` | High-res Images | Stable |

---

## Features

- **Single Unified Engine:** Zero code duplication. Switch providers with a string: `Client("reshak")` or `Client.reshak()`.
- **Dual Mode (Sync & Async):** Native asynchronous `aiohttp` engine alongside a robust synchronous `requests` client.
- **Rich Solution Models:** `Solution` models support `image_src`, `text`, and `html` for sites with formulaic or written step-by-step explanations.
- **Safe Lazy Navigation:** Await properties (`subject.books`, `book.pages`, `page.solutions`) as many times as you like without `cannot reuse already awaited coroutine` crashes.
- **Pydantic v2 Models:** Data transfer objects (`Class`, `Subject`, `Book`, `Page`, `Solution`) with strict typing.
- **Fast Search:** Server-side instant search on supported providers (e.g. Euroki) and concurrent catalog scanning on others.
- **Resilient Networking:** Explicit 15s default timeouts, modern User-Agent handling (including SSR emulation for SPAs), and protocol-relative URL normalization (`//...` &rarr; `https://...`).

---

## Installation

```bash
pip install gdzapi --upgrade
```

From source for development:

```bash
git clone https://github.com/maybewewill/gdzAPI.git
cd gdzAPI
pip install -e ".[dev]"
```

---

## Quick Start

### Asynchronous (Recommended)

```python
import asyncio
from gdzapi import AsyncClient, Provider

async def main():
    # Connect to any provider: "gdz", "reshak", "raketa", "euroki", etc.
    async with AsyncClient(Provider.RESHAK, timeout=15) as client:
        subjects = await client.get_subjects()
        math = next(s for s in subjects if "математика" in s.name.lower())

        books = await math.books
        print(f"Book: {books[0].name}")

        pages = await books[0].pages
        if pages:
            solutions = await pages[0].solutions
            print(f"Solution image: {solutions[0].image_src}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Synchronous

```python
from gdzapi import Client

# Using provider factory method
with Client.pomogalka(timeout=15) as client:
    for cls in client.classes:
        if cls.id == 5:
            print(f"Grade: {cls.name}")
            for subj in cls.subjects:
                books = subj.books
                if books:
                    print(f"Book: {books[0].name}")
                    pages = books[0].pages
                    if pages:
                        print(f"Page 1 solution: {pages[0].solutions[0].image_src}")
                break
            break
```

---

## Usage Guide

### 1. GDZ-Raketa (Text & Math Solutions)

`gdz-raketa.ru` provides full text answers with formulas in addition to images:

```python
from gdzapi import Client

client = Client.raketa()
classes = client.classes
book = classes[4].subjects[0].books[0]  # 5th grade, 1st subject, 1st book

page = book.pages[0]
solution = page.solutions[0]

print("Text explanation:", solution.text)
if solution.image_src:
    print("Illustration:", solution.image_src)
```

### 2. Reshak.ru

```python
from gdzapi import Client

client = Client.reshak()
subjects = client.subjects

for subj in subjects:
    if "математика" in subj.name.lower():
        for book in subj.books:
            print(f"{book.name} -> {book.url}")
            pages = book.pages
            if pages:
                print(f"First exercise solution: {pages[0].solutions[0].image_src}")
            break
        break
```

### 3. Euroki (Fast Search)

```python
from gdzapi import Client

client = Client.euroki()
books = client.search_books("Геометрия 8 класс")

for book in books:
    print(f"Found: {book.name}")
    pages = book.pages
    if pages:
        solutions = pages[0].solutions
        print(f"Image: {solutions[0].image_src}")
    break
```

### 4. Resh.Skysmart.ru

```python
from gdzapi import Client

client = Client.skysmart()
classes = client.classes
print(f"Loaded {len(classes)} grades from Skysmart")
```

### 5. GDZ-Putina.fun & GDZ.ltd

```python
from gdzapi import Client

# GDZ-Putina (JSON API integration)
client_putina = Client.putina()
books = client_putina.classes[0].subjects[0].books
if books:
    page = books[0].pages[0]
    print(f"Putina solution: {page.solutions[0].image_src}")

# GDZ.ltd
client_ltd = Client.ltd()
math_books = client_ltd.classes[0].subjects[0].books
if math_books:
    print(f"LTD book: {math_books[0].name}")
    print(f"LTD solution: {math_books[0].pages[0].solutions[0].image_src}")
```

### 6. Error Handling

```python
from gdzapi import Client, NetworkError, ParsingError

client = Client.gdz(timeout=10)

try:
    books = client.get_books("/non-existent-subject")
except NetworkError as e:
    print(f"Connection or HTTP status error for {e.url}: {e}")
except ParsingError as e:
    print(f"Parsing error: {e}")
```

---

## Architecture

```
gdzapi/
├── __init__.py      # Unified public API and provider factory shortcuts
├── client.py        # Single Sync & Async execution engine (Client, AsyncClient)
├── providers.py     # Declarative registry defining all 9 providers
├── models.py        # Pydantic v2 models (Class, Subject, Book, Page, Solution, AwaitableList)
├── exceptions.py    # GDZError, NetworkError, ParsingError, NotFoundError
└── utils.py         # URL normalization, DOM parsers, HTTP headers
```

### Adding a New Provider in 20 Lines

Because `gdzapi` uses a declarative provider engine, you do **not** need to create new files or rewrite sync/async boilerplate to add an 8th provider. Simply define a `ProviderSpec` in `gdzapi/providers.py`:

```python
MY_SPEC = ProviderSpec(
    name="myprovider",
    base_url="https://example.com",
    display_name="My Provider",
    extract_subjects=_my_subjects,
    extract_books=_my_books,
    extract_pages=_my_pages,
    extract_solutions=_my_solutions,
)
```

The unified `Client` and `AsyncClient` automatically provide sync, async, caching, and lazy navigation support out of the box.

---

## Testing

The test suite includes 21 isolated offline unit tests and 8 live integration tests across all 7 providers:

```bash
# Run unit tests (offline, instantaneous)
pytest -v -m "not live"

# Run all tests including live network requests
pytest -v
```

---

## License

`gdzapi` is distributed under the terms of the [MIT](https://opensource.org/licenses/MIT) license.