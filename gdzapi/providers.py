"""Declarative provider specifications for all supported GDZ websites."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup as BS

from .models import Book, Class, Page, Solution, Subject
from .utils import clean_text, normalize_url, safe_text


@dataclass
class ProviderSpec:
    """Declarative specification for a GDZ source provider."""

    name: str
    base_url: str
    display_name: str
    headers: Optional[Dict[str, str]] = None
    classes_url: str = "/"
    subjects_url: str = "/"
    extract_classes: Optional[Callable[[BS, str, Any], List[Class]]] = None
    extract_subjects: Optional[Callable[[BS, str, Any], List[Subject]]] = None
    extract_books: Optional[Callable[[BS, str, Any], List[Book]]] = None
    extract_pages: Optional[Callable[[BS, str, Any], List[Page]]] = None
    extract_solutions: Optional[Callable[[BS, str, Any], List[Solution]]] = None
    search_path_template: Optional[str] = None
    extract_search_books: Optional[Callable[[BS, str, Any], List[Book]]] = None


# ---------------------------------------------------------------------------
# 1. GDZ.ru
# ---------------------------------------------------------------------------

def _gdz_classes(soup: BS, base_url: str, client: Any) -> List[Class]:
    classes_sel = "body > div > div.page > aside > div.sidebar__main > div > ul > li"
    class_elements = soup.select(classes_sel)
    classes: List[Class] = []

    for id_, class_el in enumerate(class_elements, start=1):
        name_el = class_el.select_one("a")
        name = clean_text(name_el.text) if name_el else f"{id_} класс"

        subjects: List[Subject] = []
        sub_id = 1
        for sub_el in class_el.select("ul li a"):
            sub_text = clean_text(sub_el.text)
            if not sub_text or sub_text == name or "все предметы" in sub_text.lower():
                continue
            subjects.append(
                Subject(id=sub_id, name=sub_text, url=sub_el.get("href") or "").bind_client(client)
            )
            sub_id += 1

        classes.append(Class(id=id_, name=name, url=f"/class-{id_}", subjects=subjects))

    return classes


def _gdz_subjects(soup: BS, base_url: str, client: Any) -> List[Subject]:
    subj_sel = "body > div.layout > div.page > main > table > tbody > tr > td.table-section-heading > a"
    subjects: List[Subject] = []
    for id_, el in enumerate(soup.select(subj_sel), start=1):
        subjects.append(
            Subject(id=id_, name=clean_text(el.text), url=el.get("href") or "").bind_client(client)
        )
    return subjects


def _gdz_books(soup: BS, base_url: str, client: Any) -> List[Book]:
    books_sel = "body > div > div.page > main > ul.book__list > li > a"
    books: List[Book] = []
    for id_, el in enumerate(soup.select(books_sel), start=1):
        title = el.get("title") or safe_text(el, "div > p")
        spans = el.select("div > p > span")
        authors = [clean_text(s) for s in spans[0].text.split(", ")] if spans else []
        books.append(
            Book(
                id=id_,
                name=clean_text(title),
                url=el.get("href") or "",
                authors=authors,
            ).bind_client(client)
        )
    return books


def _gdz_pages(soup: BS, base_url: str, client: Any) -> List[Page]:
    container = soup.select_one("body > div > div.page > main > div.task__list.js-tasks-container")
    if not container:
        return []
    pages: List[Page] = []
    for id_, el in enumerate(container.select("div > a"), start=1):
        pages.append(
            Page(id=id_, number=clean_text(el.text), url=el.get("href") or "").bind_client(client)
        )
    return pages


def _gdz_solutions(soup: BS, base_url: str, client: Any) -> List[Solution]:
    gdz_sel = "body > div.layout > div.page > main > figure > div.task-img-container > div > img"
    solutions: List[Solution] = []
    for id_, img in enumerate(soup.select(gdz_sel), start=1):
        src = img.get("src") or img.get("data-src") or ""
        alt = img.get("alt") or ""
        title = alt.split("  ")[-1].strip() if alt else None
        solutions.append(
            Solution(id=id_, title=title, image_src=normalize_url(base_url, src))
        )
    return solutions


GDZ_SPEC = ProviderSpec(
    name="gdz",
    base_url="https://www.gdz.ru",
    display_name="GDZ.ru",
    extract_classes=_gdz_classes,
    extract_subjects=_gdz_subjects,
    extract_books=_gdz_books,
    extract_pages=_gdz_pages,
    extract_solutions=_gdz_solutions,
)


# ---------------------------------------------------------------------------
# 2. Euroki.org
# ---------------------------------------------------------------------------

def _euroki_classes(soup: BS, base_url: str, client: Any) -> List[Class]:
    classes: List[Class] = []
    for id_, class_el in enumerate(soup.select("#menuwka_new > ul.primary > li"), start=1):
        name_el = class_el.select_one("a")
        name = clean_text(name_el.text) if name_el else f"{id_} класс"
        link = (name_el.get("href") if name_el else None) or f"/gdz/ru/vse/{id_}_klass"

        subjects: List[Subject] = []
        for sub_id, sub_el in enumerate(class_el.select("ul > li.sbjcts > a"), start=1):
            subjects.append(
                Subject(
                    id=sub_id,
                    name=sub_el.get("title") or clean_text(sub_el.text),
                    url=sub_el.get("href") or "",
                ).bind_client(client)
            )

        classes.append(Class(id=id_, name=name, url=link, subjects=subjects))
    return classes


def _euroki_subjects(soup: BS, base_url: str, client: Any) -> List[Subject]:
    subj_sel = "body > div.bg_main > div.ads > div.ft_menu.clearfix > div:nth-child(2) > ul > li > a"
    subjects: List[Subject] = []
    for id_, el in enumerate(soup.select(subj_sel), start=1):
        subjects.append(
            Subject(id=id_, name=clean_text(el.text), url=el.get("href") or "").bind_client(client)
        )
    return subjects


def _euroki_books(soup: BS, base_url: str, client: Any) -> List[Book]:
    sel = "body > div.bg_main > div.device_desktop.clearfix > div.dsk_main > div.content > ul > li > a, .content ul > li > a"
    books: List[Book] = []
    for id_, el in enumerate(soup.select(sel), start=1):
        title = safe_text(el, "div.rghpnl > div.bttl") or el.get("title") or clean_text(el.text)
        authors_span = el.select_one("div.rghpnl > div.book_description > div.book_mt > div > span")
        authors = [clean_text(a) for a in authors_span.text.split(", ")] if authors_span else []
        books.append(
            Book(
                id=id_,
                name=clean_text(title),
                url=el.get("href") or "",
                authors=authors,
            ).bind_client(client)
        )
    return books


def _euroki_pages(soup: BS, base_url: str, client: Any) -> List[Page]:
    sel = ".book-navigation__panel a, div.txt_version a, section.book-navigation a"
    pages: List[Page] = []
    for id_, el in enumerate(soup.select(sel), start=1):
        pages.append(
            Page(
                id=id_,
                number=clean_text(el.text) or str(id_),
                url=el.get("href") or "",
            ).bind_client(client)
        )
    return pages


def _euroki_solutions(soup: BS, base_url: str, client: Any) -> List[Solution]:
    sel = "img.gdz_image, #txt_cont img.gdz_image, .content.one_page img.gdz_image, #txt_cont > p > img"
    solutions: List[Solution] = []
    for id_, img in enumerate(soup.select(sel), start=1):
        src = img.get("data-src") or img.get("data-original") or img.get("src") or ""
        if not src or src.startswith("data:image"):
            continue
        solutions.append(
            Solution(id=id_, image_src=normalize_url(base_url, src), title=img.get("alt"))
        )
    return solutions


def _euroki_search(soup: BS, base_url: str, client: Any) -> List[Book]:
    books: List[Book] = []
    for id_, a in enumerate(soup.select(".content ul > li > a"), start=1):
        books.append(
            Book(
                id=id_,
                name=clean_text(a.text),
                url=normalize_url(base_url, a.get("href") or ""),
            ).bind_client(client)
        )
    return books


EUROKI_SPEC = ProviderSpec(
    name="euroki",
    base_url="https://euroki.org",
    display_name="Euroki.org",
    extract_classes=_euroki_classes,
    extract_subjects=_euroki_subjects,
    extract_books=_euroki_books,
    extract_pages=_euroki_pages,
    extract_solutions=_euroki_solutions,
    search_path_template="/search?q={query}",
    extract_search_books=_euroki_search,
)


# ---------------------------------------------------------------------------
# 3. MegaResheba.ru
# ---------------------------------------------------------------------------

def _megaresheba_classes(soup: BS, base_url: str, client: Any) -> List[Class]:
    classes: List[Class] = []
    for id_, class_el in enumerate(soup.select(".mainMenu.desktopMenu > ul > li, .mainMenu ul > li"), start=1):
        name_el = class_el.select_one("a")
        name = clean_text(name_el.text) if name_el else f"{id_} класс"
        link = name_el.get("href") if name_el else f"/class-{id_}"

        subjects: List[Subject] = []
        for sub_id, sub_el in enumerate(class_el.select("a")[1:], start=1):
            subjects.append(
                Subject(id=sub_id, name=clean_text(sub_el.text), url=sub_el.get("href") or "").bind_client(client)
            )

        classes.append(Class(id=id_, name=name, url=link, subjects=subjects))
    return classes


def _megaresheba_subjects(soup: BS, base_url: str, client: Any) -> List[Subject]:
    subjects: List[Subject] = []
    for id_, el in enumerate(soup.select(".indexTable > li > div > a, .indexTable a"), start=1):
        subjects.append(
            Subject(id=id_, name=clean_text(el.text), url=el.get("href") or "").bind_client(client)
        )
    return subjects


def _megaresheba_books(soup: BS, base_url: str, client: Any) -> List[Book]:
    books: List[Book] = []
    for id_, el in enumerate(soup.select(".content ul > li > a.book, a.book"), start=1):
        title = safe_text(el, "div.bookDescription > div.bigText.bolder") or el.get("title") or clean_text(el.text)
        author_spans = el.select("div.m5 > span")
        authors = [clean_text(x) for x in author_spans[:-1]] if len(author_spans) > 1 else []
        books.append(
            Book(
                id=id_,
                name=clean_text(title),
                url=el.get("href") or "",
                authors=authors,
            ).bind_client(client)
        )
    return books


def _megaresheba_pages(soup: BS, base_url: str, client: Any) -> List[Page]:
    pages: List[Page] = []
    for id_, el in enumerate(soup.select("#tasks > div > div > a, .tasks a, #tasks a"), start=1):
        pages.append(
            Page(
                id=id_,
                number=safe_text(el, "span") or clean_text(el.text) or str(id_),
                url=el.get("href") or "",
            ).bind_client(client)
        )
    return pages


def _megaresheba_solutions(soup: BS, base_url: str, client: Any) -> List[Solution]:
    solutions: List[Solution] = []
    for id_, img in enumerate(soup.select("#task > div > div > img, #task img, .task-image img"), start=1):
        src = img.get("src") or img.get("data-src") or ""
        if not src or src.startswith("data:image"):
            continue
        solutions.append(
            Solution(id=id_, image_src=normalize_url(base_url, src), title=img.get("alt"))
        )
    return solutions


MEGARESHEBA_SPEC = ProviderSpec(
    name="megaresheba",
    base_url="https://megaresheba.ru",
    display_name="MegaResheba.ru",
    extract_classes=_megaresheba_classes,
    extract_subjects=_megaresheba_subjects,
    extract_books=_megaresheba_books,
    extract_pages=_megaresheba_pages,
    extract_solutions=_megaresheba_solutions,
)


# ---------------------------------------------------------------------------
# 4. GDZ-Raketa.ru
# ---------------------------------------------------------------------------

def _raketa_classes(soup: BS, base_url: str, client: Any) -> List[Class]:
    classes: List[Class] = []
    # Collect grade links: e.g. /{subject}/{grade}-klass/
    grade_links: Dict[int, List[Subject]] = {i: [] for i in range(1, 12)}
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        text = clean_text(a.text)
        for g in range(1, 12):
            if f"/{g}-klass/" in href or f"/{g}klass/" in href:
                subj_name = href.strip("/").split("/")[0].replace("-", " ").capitalize()
                grade_links[g].append(
                    Subject(id=len(grade_links[g]) + 1, name=subj_name, url=href).bind_client(client)
                )
                break

    for g in range(1, 12):
        # deduplicate subjects
        seen = set()
        unique_subjs: List[Subject] = []
        for s in grade_links[g]:
            if s.name not in seen:
                seen.add(s.name)
                unique_subjs.append(s)
        classes.append(Class(id=g, name=f"{g} класс", url=f"/klass-{g}/", subjects=unique_subjs))
    return classes


def _raketa_subjects(soup: BS, base_url: str, client: Any) -> List[Subject]:
    seen = set()
    subjects: List[Subject] = []
    sub_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "klass" in href and href.count("/") >= 2:
            parts = href.strip("/").split("/")
            subj_raw = parts[0]
            if subj_raw not in seen:
                seen.add(subj_raw)
                subj_name = subj_raw.replace("-", " ").capitalize()
                subjects.append(
                    Subject(id=sub_id, name=subj_name, url=f"/{subj_raw}/").bind_client(client)
                )
                sub_id += 1
    return subjects


def _raketa_books(soup: BS, base_url: str, client: Any) -> List[Book]:
    books: List[Book] = []
    book_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if href.count("/") >= 3 and not href.endswith("-klass/"):
            title = clean_text(a.text)
            if not title or len(title) < 3 or "главная" in title.lower():
                continue
            books.append(
                Book(id=book_id, name=title, url=href, authors=[]).bind_client(client)
            )
            book_id += 1
    return books


def _raketa_pages(soup: BS, base_url: str, client: Any) -> List[Page]:
    pages: List[Page] = []
    p_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        text = clean_text(a.text)
        if any(term in href for term in ["stranica", "nomer", "zadanie", "chast"]):
            pages.append(
                Page(id=p_id, number=text or str(p_id), url=href).bind_client(client)
            )
            p_id += 1
    return pages


def _raketa_solutions(soup: BS, base_url: str, client: Any) -> List[Solution]:
    solutions: List[Solution] = []
    desc = soup.select_one(".description, .page-content")
    solution_text = clean_text(desc.text) if desc else ""
    solution_html = str(desc) if desc else None

    # Collect images
    imgs = [
        img.get("data-src") or img.get("src")
        for img in soup.find_all("img")
        if img.get("src") and not any(x in img.get("src") for x in ["logo", "icon", "visa", "footer", "stars", "cloud", "gift", "author"])
    ]
    img_src = normalize_url(base_url, imgs[0]) if imgs else None

    solutions.append(
        Solution(
            id=1,
            title="Решение",
            image_src=img_src,
            text=solution_text,
            html=solution_html,
        )
    )
    return solutions


RAKETA_SPEC = ProviderSpec(
    name="raketa",
    base_url="https://gdz-raketa.ru",
    display_name="GDZ-Raketa.ru",
    extract_classes=_raketa_classes,
    extract_subjects=_raketa_subjects,
    extract_books=_raketa_books,
    extract_pages=_raketa_pages,
    extract_solutions=_raketa_solutions,
)


# ---------------------------------------------------------------------------
# 5. Reshak.ru
# ---------------------------------------------------------------------------

def _reshak_classes(soup: BS, base_url: str, client: Any) -> List[Class]:
    classes: List[Class] = []
    for g in range(1, 12):
        subjs: List[Subject] = []
        sub_id = 1
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            text = clean_text(a.text)
            if f"{g}klass_" in href:
                subjs.append(
                    Subject(id=sub_id, name=text or f"Предмет {sub_id}", url=href).bind_client(client)
                )
                sub_id += 1
        classes.append(Class(id=g, name=f"{g} класс", url=f"/tag/{g}klass.html", subjects=subjs))
    return classes


def _reshak_subjects(soup: BS, base_url: str, client: Any) -> List[Subject]:
    subjects: List[Subject] = []
    seen = set()
    sub_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        text = clean_text(a.text)
        if "/tag/" in href and "klass_" in href and text not in seen:
            seen.add(text)
            subjects.append(
                Subject(id=sub_id, name=text, url=href).bind_client(client)
            )
            sub_id += 1
    return subjects


def _reshak_books(soup: BS, base_url: str, client: Any) -> List[Book]:
    books: List[Book] = []
    b_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "/reshebniki/" in href and href.endswith(".html"):
            title = clean_text(a.text)
            if title and len(title) > 3:
                books.append(
                    Book(id=b_id, name=title, url=href, authors=[]).bind_client(client)
                )
                b_id += 1
    return books


def _reshak_pages(soup: BS, base_url: str, client: Any) -> List[Page]:
    pages: List[Page] = []
    p_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        text = clean_text(a.text)
        if "otvet=" in href:
            pages.append(
                Page(id=p_id, number=text or str(p_id), url=href).bind_client(client)
            )
            p_id += 1
    return pages


def _reshak_solutions(soup: BS, base_url: str, client: Any) -> List[Solution]:
    solutions: List[Solution] = []
    img_elements = soup.select(".pic_otvet1 img, .otvet_pic img, img[src*='/reshebniki/']")
    for id_, img in enumerate(img_elements, start=1):
        src = img.get("src") or ""
        solutions.append(
            Solution(id=id_, image_src=normalize_url(base_url, src), title=img.get("alt"))
        )
    return solutions


RESHAK_SPEC = ProviderSpec(
    name="reshak",
    base_url="https://reshak.ru",
    display_name="Reshak.ru",
    extract_classes=_reshak_classes,
    extract_subjects=_reshak_subjects,
    extract_books=_reshak_books,
    extract_pages=_reshak_pages,
    extract_solutions=_reshak_solutions,
)


# ---------------------------------------------------------------------------
# 6. Pomogalka.me
# ---------------------------------------------------------------------------

def _pomogalka_classes(soup: BS, base_url: str, client: Any) -> List[Class]:
    classes: List[Class] = []
    for g in range(1, 12):
        subjs: List[Subject] = []
        sub_id = 1
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if href.startswith(f"/{g}-klass/") and href.count("/") == 3:
                subj_name = href.split("/")[2].replace("-", " ").capitalize()
                subjs.append(
                    Subject(id=sub_id, name=subj_name, url=href).bind_client(client)
                )
                sub_id += 1
        classes.append(Class(id=g, name=f"{g} класс", url=f"/{g}-klass/", subjects=subjs))
    return classes


def _pomogalka_subjects(soup: BS, base_url: str, client: Any) -> List[Subject]:
    seen = set()
    subjects: List[Subject] = []
    sub_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if href.count("/") == 3 and "-klass/" in href:
            subj_raw = href.split("/")[2]
            if subj_raw not in seen:
                seen.add(subj_raw)
                subjects.append(
                    Subject(id=sub_id, name=subj_raw.replace("-", " ").capitalize(), url=href).bind_client(client)
                )
                sub_id += 1
    return subjects


def _pomogalka_books(soup: BS, base_url: str, client: Any) -> List[Book]:
    books: List[Book] = []
    b_id = 1
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if href.count("/") == 4 and "-klass/" in href:
            text = clean_text(a.text)
            if href not in seen and text and text != "Смотреть":
                seen.add(href)
                books.append(
                    Book(id=b_id, name=text, url=href, authors=[]).bind_client(client)
                )
                b_id += 1
    return books


def _pomogalka_pages(soup: BS, base_url: str, client: Any) -> List[Page]:
    pages: List[Page] = []
    p_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        text = clean_text(a.text)
        if any(term in href for term in ["stranica-", "nomer-", "zadanie-", "urok-"]) or (href.count("/") >= 5 and any(c.isdigit() for c in href)):
            pages.append(
                Page(id=p_id, number=text or str(p_id), url=href).bind_client(client)
            )
            p_id += 1
    return pages


def _pomogalka_solutions(soup: BS, base_url: str, client: Any) -> List[Solution]:
    solutions: List[Solution] = []
    imgs = soup.select(".task-txt img, img[src*='/img-res/']")
    for id_, img in enumerate(imgs, start=1):
        src = img.get("src") or img.get("data-src") or ""
        solutions.append(
            Solution(id=id_, image_src=normalize_url(base_url, src), title=img.get("alt"))
        )
    return solutions


POMOGALKA_SPEC = ProviderSpec(
    name="pomogalka",
    base_url="https://pomogalka.me",
    display_name="Pomogalka.me",
    extract_classes=_pomogalka_classes,
    extract_subjects=_pomogalka_subjects,
    extract_books=_pomogalka_books,
    extract_pages=_pomogalka_pages,
    extract_solutions=_pomogalka_solutions,
)


# ---------------------------------------------------------------------------
# 7. Resh.Skysmart.ru
# ---------------------------------------------------------------------------

SKYSMART_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _skysmart_classes(soup: BS, base_url: str, client: Any) -> List[Class]:
    classes: List[Class] = []
    common_subjects = [
        "Математика", "Алгебра", "Геометрия", "Русский язык",
        "Английский язык", "Физика", "Химия", "Биология", "История"
    ]
    for g in range(1, 12):
        subjs = [
            Subject(id=idx, name=name, url=f"/{g}-klass/{name.lower()}/").bind_client(client)
            for idx, name in enumerate(common_subjects, start=1)
        ]
        classes.append(Class(id=g, name=f"{g} класс", url=f"/{g}-klass/", subjects=subjs))
    return classes


def _skysmart_subjects(soup: BS, base_url: str, client: Any) -> List[Subject]:
    common_subjects = [
        "Математика", "Алгебра", "Геометрия", "Русский язык",
        "Английский язык", "Физика", "Химия", "Биология", "История"
    ]
    return [
        Subject(id=idx, name=name, url=f"/matematika/").bind_client(client)
        for idx, name in enumerate(common_subjects, start=1)
    ]


def _skysmart_books(soup: BS, base_url: str, client: Any) -> List[Book]:
    books: List[Book] = []
    b_id = 1
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "-klass/" in href and href.count("/") >= 3 and href not in seen:
            seen.add(href)
            text = clean_text(a.text) or href.strip("/").split("/")[-1]
            books.append(
                Book(id=b_id, name=text, url=href, authors=[]).bind_client(client)
            )
            b_id += 1
    return books


def _skysmart_pages(soup: BS, base_url: str, client: Any) -> List[Page]:
    pages: List[Page] = []
    p_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "nomer-" in href:
            text = clean_text(a.text)
            pages.append(
                Page(id=p_id, number=text or str(p_id), url=href).bind_client(client)
            )
            p_id += 1
    return pages


def _skysmart_solutions(soup: BS, base_url: str, client: Any) -> List[Solution]:
    solutions: List[Solution] = []
    imgs = [
        img.get("src") or img.get("data-src")
        for img in soup.find_all("img")
        if img.get("src") and not any(x in img.get("src") for x in [".svg", "logo", "favicon", "avatar"])
    ]
    for idx, src in enumerate(imgs, start=1):
        solutions.append(
            Solution(id=idx, image_src=normalize_url(base_url, src), title=f"Шаг {idx}")
        )
    return solutions


SKYSMART_SPEC = ProviderSpec(
    name="skysmart",
    base_url="https://resh.skysmart.ru",
    display_name="Skysmart",
    headers=SKYSMART_HEADERS,
    extract_classes=_skysmart_classes,
    extract_subjects=_skysmart_subjects,
    extract_books=_skysmart_books,
    extract_pages=_skysmart_pages,
    extract_solutions=_skysmart_solutions,
)


# ---------------------------------------------------------------------------
# 8. GDZ-Putina.fun
# ---------------------------------------------------------------------------

def _putina_classes(soup: BS, base_url: str, client: Any) -> List[Class]:
    classes: List[Class] = []
    for g in range(1, 12):
        subjs: List[Subject] = []
        sub_id = 1
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if href.startswith(f"/klass-{g}/") and href.count("/") == 2:
                subj_name = clean_text(a.text) or href.split("/")[-1].replace("-", " ").capitalize()
                subjs.append(
                    Subject(id=sub_id, name=subj_name, url=href).bind_client(client)
                )
                sub_id += 1
        classes.append(Class(id=g, name=f"{g} класс", url=f"/klass-{g}", subjects=subjs))
    return classes


def _putina_subjects(soup: BS, base_url: str, client: Any) -> List[Subject]:
    seen = set()
    subjects: List[Subject] = []
    sub_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "/klass-" in href and href.count("/") == 2:
            subj_slug = href.split("/")[-1]
            if subj_slug not in seen:
                seen.add(subj_slug)
                subj_name = clean_text(a.text) or subj_slug.replace("-", " ").capitalize()
                subjects.append(
                    Subject(id=sub_id, name=subj_name, url=href).bind_client(client)
                )
                sub_id += 1
    return subjects


def _putina_books(soup: BS, base_url: str, client: Any) -> List[Book]:
    books: List[Book] = []
    b_id = 1
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "/klass-" in href and href.count("/") == 3 and href not in seen:
            seen.add(href)
            text = clean_text(a.text)
            if text and len(text) > 3 and not text.isdigit():
                books.append(
                    Book(id=b_id, name=text, url=href, authors=[]).bind_client(client)
                )
                b_id += 1
    return books


def _putina_pages(soup: BS, base_url: str, client: Any) -> List[Page]:
    pages: List[Page] = []
    p_id = 1
    tasks_div = soup.select_one(".tasks")
    book_path = tasks_div.get("data-url", "") if tasks_div else ""

    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "#task?t=" in href:
            task_param = href.split("#task?t=")[-1]
            json_url = f"/json{book_path}/{task_param}" if book_path else href
            pages.append(
                Page(id=p_id, number=clean_text(a.text) or str(p_id), url=json_url).bind_client(client)
            )
            p_id += 1
    return pages


def _putina_solutions(soup: BS, base_url: str, client: Any) -> List[Solution]:
    import json
    solutions: List[Solution] = []
    raw_text = soup.text.strip()
    if raw_text.startswith("{") and raw_text.endswith("}"):
        try:
            data = json.loads(raw_text)
            for edition in data.get("editions", []):
                for id_, img_obj in enumerate(edition.get("images", []), start=1):
                    img_url = img_obj.get("url")
                    if img_url:
                        solutions.append(
                            Solution(id=id_, image_src=normalize_url(base_url, img_url), title=img_obj.get("title"))
                        )
            if solutions:
                return solutions
        except Exception:
            pass

    imgs = [
        img.get("src") or img.get("data-src")
        for img in soup.find_all("img")
        if img.get("src") and "ajax.gif" not in img.get("src")
    ]
    for id_, src in enumerate(imgs, start=1):
        solutions.append(
            Solution(id=id_, image_src=normalize_url(base_url, src))
        )
    return solutions


PUTINA_SPEC = ProviderSpec(
    name="putina",
    base_url="https://gdz-putina.fun",
    display_name="GDZ-Putina.fun",
    extract_classes=_putina_classes,
    extract_subjects=_putina_subjects,
    extract_books=_putina_books,
    extract_pages=_putina_pages,
    extract_solutions=_putina_solutions,
)


# ---------------------------------------------------------------------------
# 9. GDZ.ltd
# ---------------------------------------------------------------------------

def _ltd_classes(soup: BS, base_url: str, client: Any) -> List[Class]:
    classes: List[Class] = []
    for g in range(1, 12):
        subjs: List[Subject] = []
        sub_id = 1
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if href.startswith(f"/{g}-class/") and href.count("/") == 3:
                subj_name = href.split("/")[2].replace("-", " ").capitalize()
                subjs.append(
                    Subject(id=sub_id, name=subj_name, url=href).bind_client(client)
                )
                sub_id += 1
        classes.append(Class(id=g, name=f"{g} класс", url=f"/{g}-class/", subjects=subjs))
    return classes


def _ltd_subjects(soup: BS, base_url: str, client: Any) -> List[Subject]:
    seen = set()
    subjects: List[Subject] = []
    sub_id = 1
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "-class/" in href and href.count("/") == 3:
            subj_slug = href.split("/")[2]
            if subj_slug not in seen:
                seen.add(subj_slug)
                subjects.append(
                    Subject(id=sub_id, name=subj_slug.replace("-", " ").capitalize(), url=href).bind_client(client)
                )
                sub_id += 1
    return subjects


def _ltd_books(soup: BS, base_url: str, client: Any) -> List[Book]:
    books: List[Book] = []
    b_id = 1
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "-class/" in href and href.count("/") == 4 and href not in seen:
            seen.add(href)
            text = clean_text(a.text)
            if text and len(text) > 3:
                books.append(
                    Book(id=b_id, name=text, url=href, authors=[]).bind_client(client)
                )
                b_id += 1
    return books


def _ltd_pages(soup: BS, base_url: str, client: Any) -> List[Page]:
    pages: List[Page] = []
    p_id = 1
    for el in soup.select(".image_load"):
        img_path = el.get("img") or ""
        text = clean_text(el.text) or str(p_id)
        if img_path:
            full_img = f"{img_path}.jpg" if not img_path.endswith((".jpg", ".png")) else img_path
            pages.append(
                Page(id=p_id, number=text, url=full_img).bind_client(client)
            )
            p_id += 1
    return pages


def _ltd_solutions(soup: BS, base_url: str, client: Any) -> List[Solution]:
    img_elements = soup.select("#main-image img, .image_load img, img[src*='/exercise/'], img[src*='/content/']")
    solutions: List[Solution] = []
    for id_, img in enumerate(img_elements, start=1):
        src = img.get("src") or ""
        solutions.append(
            Solution(id=id_, image_src=normalize_url(base_url, src))
        )
    return solutions


LTD_SPEC = ProviderSpec(
    name="ltd",
    base_url="https://gdz.ltd",
    display_name="GDZ.ltd",
    extract_classes=_ltd_classes,
    extract_subjects=_ltd_subjects,
    extract_books=_ltd_books,
    extract_pages=_ltd_pages,
    extract_solutions=_ltd_solutions,
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

PROVIDERS: Dict[str, ProviderSpec] = {
    "gdz": GDZ_SPEC,
    "euroki": EUROKI_SPEC,
    "megaresheba": MEGARESHEBA_SPEC,
    "raketa": RAKETA_SPEC,
    "reshak": RESHAK_SPEC,
    "pomogalka": POMOGALKA_SPEC,
    "skysmart": SKYSMART_SPEC,
    "putina": PUTINA_SPEC,
    "ltd": LTD_SPEC,
}


class Provider:
    """Provider identifiers."""

    GDZ = "gdz"
    EUROKI = "euroki"
    MEGARESHEBA = "megaresheba"
    RAKETA = "raketa"
    RESHAK = "reshak"
    POMOGALKA = "pomogalka"
    SKYSMART = "skysmart"
    PUTINA = "putina"
    LTD = "ltd"


def get_provider_spec(name_or_spec: str | ProviderSpec) -> ProviderSpec:
    """Retrieve ProviderSpec by name or return spec object."""
    if isinstance(name_or_spec, ProviderSpec):
        return name_or_spec
    key = name_or_spec.lower().strip()
    if key not in PROVIDERS:
        avail = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{name_or_spec}'. Available providers: {avail}")
    return PROVIDERS[key]
