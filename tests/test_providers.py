"""Unit tests for all 7 declarative provider specifications."""

from __future__ import annotations

from bs4 import BeautifulSoup as BS
import pytest

from gdzapi.client import Client
from gdzapi.providers import (
    EUROKI_SPEC,
    GDZ_SPEC,
    LTD_SPEC,
    MEGARESHEBA_SPEC,
    POMOGALKA_SPEC,
    PUTINA_SPEC,
    RAKETA_SPEC,
    RESHAK_SPEC,
    SKYSMART_SPEC,
    get_provider_spec,
)


def test_get_provider_spec():
    spec = get_provider_spec("gdz")
    assert spec.name == "gdz"
    spec2 = get_provider_spec("reshak")
    assert spec2.name == "reshak"
    with pytest.raises(ValueError):
        get_provider_spec("unknown_provider")


def test_gdz_spec_parsing(gdz_main_html, gdz_books_html, gdz_pages_html, gdz_solution_html):
    client = Client.gdz()
    soup_main = BS(gdz_main_html, "html.parser")
    classes = GDZ_SPEC.extract_classes(soup_main, GDZ_SPEC.base_url, client)
    assert len(classes) == 2
    assert "1 класс" in classes[0].name

    subjects = GDZ_SPEC.extract_subjects(soup_main, GDZ_SPEC.base_url, client)
    assert len(subjects) == 2
    assert subjects[0].name == "Математика"

    soup_books = BS(gdz_books_html, "html.parser")
    books = GDZ_SPEC.extract_books(soup_books, GDZ_SPEC.base_url, client)
    assert len(books) == 2
    assert "Моро" in books[0].name

    soup_pages = BS(gdz_pages_html, "html.parser")
    pages = GDZ_SPEC.extract_pages(soup_pages, GDZ_SPEC.base_url, client)
    assert len(pages) == 2
    assert pages[0].number == "1"

    soup_sol = BS(gdz_solution_html, "html.parser")
    solutions = GDZ_SPEC.extract_solutions(soup_sol, GDZ_SPEC.base_url, client)
    assert len(solutions) == 1
    assert "https://gdz.ru" in solutions[0].image_src


def test_euroki_spec_parsing(euroki_main_html, euroki_pages_html, euroki_solution_html):
    client = Client.euroki()
    soup_main = BS(euroki_main_html, "html.parser")
    classes = EUROKI_SPEC.extract_classes(soup_main, EUROKI_SPEC.base_url, client)
    assert len(classes) == 1
    assert "11 класс" in classes[0].name

    subjects = EUROKI_SPEC.extract_subjects(soup_main, EUROKI_SPEC.base_url, client)
    assert len(subjects) == 2

    soup_pages = BS(euroki_pages_html, "html.parser")
    pages = EUROKI_SPEC.extract_pages(soup_pages, EUROKI_SPEC.base_url, client)
    assert len(pages) == 2

    soup_sol = BS(euroki_solution_html, "html.parser")
    solutions = EUROKI_SPEC.extract_solutions(soup_sol, EUROKI_SPEC.base_url, client)
    assert len(solutions) == 1
    assert "imgs.euroki.org" in solutions[0].image_src


def test_megaresheba_spec_parsing(megaresheba_main_html, megaresheba_pages_html, megaresheba_solution_html):
    client = Client.megaresheba()
    soup_main = BS(megaresheba_main_html, "html.parser")
    classes = MEGARESHEBA_SPEC.extract_classes(soup_main, MEGARESHEBA_SPEC.base_url, client)
    assert len(classes) == 1

    subjects = MEGARESHEBA_SPEC.extract_subjects(soup_main, MEGARESHEBA_SPEC.base_url, client)
    assert len(subjects) == 1

    soup_pages = BS(megaresheba_pages_html, "html.parser")
    pages = MEGARESHEBA_SPEC.extract_pages(soup_pages, MEGARESHEBA_SPEC.base_url, client)
    assert len(pages) == 2

    soup_sol = BS(megaresheba_solution_html, "html.parser")
    solutions = MEGARESHEBA_SPEC.extract_solutions(soup_sol, MEGARESHEBA_SPEC.base_url, client)
    assert len(solutions) == 1


def test_raketa_spec_parsing(raketa_html):
    client = Client.raketa()
    soup = BS(raketa_html, "html.parser")

    classes = RAKETA_SPEC.extract_classes(soup, RAKETA_SPEC.base_url, client)
    assert len(classes) == 11
    assert classes[0].name == "1 класс"

    books = RAKETA_SPEC.extract_books(soup, RAKETA_SPEC.base_url, client)
    assert len(books) >= 1
    assert "Моро" in books[0].name

    pages = RAKETA_SPEC.extract_pages(soup, RAKETA_SPEC.base_url, client)
    assert len(pages) >= 1

    solutions = RAKETA_SPEC.extract_solutions(soup, RAKETA_SPEC.base_url, client)
    assert len(solutions) == 1
    assert "1, 2, 3, 4" in solutions[0].text
    assert solutions[0].image_src is not None


def test_reshak_spec_parsing(reshak_html):
    client = Client.reshak()
    soup = BS(reshak_html, "html.parser")

    subjects = RESHAK_SPEC.extract_subjects(soup, RESHAK_SPEC.base_url, client)
    assert len(subjects) == 1
    assert subjects[0].name == "Математика"

    books = RESHAK_SPEC.extract_books(soup, RESHAK_SPEC.base_url, client)
    assert len(books) == 1
    assert "Мерзляк" in books[0].name

    pages = RESHAK_SPEC.extract_pages(soup, RESHAK_SPEC.base_url, client)
    assert len(pages) == 1
    assert pages[0].number == "1"

    solutions = RESHAK_SPEC.extract_solutions(soup, RESHAK_SPEC.base_url, client)
    assert len(solutions) == 1
    assert "images1/1.png" in solutions[0].image_src


def test_pomogalka_spec_parsing(pomogalka_html):
    client = Client.pomogalka()
    soup = BS(pomogalka_html, "html.parser")

    subjects = POMOGALKA_SPEC.extract_subjects(soup, POMOGALKA_SPEC.base_url, client)
    assert len(subjects) == 1
    assert subjects[0].name == "Matematika"

    books = POMOGALKA_SPEC.extract_books(soup, POMOGALKA_SPEC.base_url, client)
    assert len(books) == 1
    assert "Моро" in books[0].name

    pages = POMOGALKA_SPEC.extract_pages(soup, POMOGALKA_SPEC.base_url, client)
    assert len(pages) == 1

    solutions = POMOGALKA_SPEC.extract_solutions(soup, POMOGALKA_SPEC.base_url, client)
    assert len(solutions) == 1
    assert "img-res" in solutions[0].image_src


def test_skysmart_spec():
    client = Client.skysmart()
    soup = BS("<html><body></body></html>", "html.parser")
    classes = SKYSMART_SPEC.extract_classes(soup, SKYSMART_SPEC.base_url, client)
    assert len(classes) == 11
    assert len(classes[0].subjects) > 0


def test_putina_spec_parsing(putina_html, putina_json):
    client = Client.putina()
    soup = BS(putina_html, "html.parser")

    subjects = PUTINA_SPEC.extract_subjects(soup, PUTINA_SPEC.base_url, client)
    assert len(subjects) == 1
    assert "Математика" in subjects[0].name

    books = PUTINA_SPEC.extract_books(soup, PUTINA_SPEC.base_url, client)
    assert len(books) == 1
    assert "Моро" in books[0].name

    pages = PUTINA_SPEC.extract_pages(soup, PUTINA_SPEC.base_url, client)
    assert len(pages) == 1
    assert pages[0].number == "4"

    soup_json = BS(putina_json, "html.parser")
    solutions = PUTINA_SPEC.extract_solutions(soup_json, PUTINA_SPEC.base_url, client)
    assert len(solutions) == 1
    assert "sample.jpg" in solutions[0].image_src


def test_ltd_spec_parsing(ltd_html):
    client = Client.ltd()
    soup = BS(ltd_html, "html.parser")

    subjects = LTD_SPEC.extract_subjects(soup, LTD_SPEC.base_url, client)
    assert len(subjects) == 1
    assert "Matematika" in subjects[0].name

    books = LTD_SPEC.extract_books(soup, LTD_SPEC.base_url, client)
    assert len(books) == 1
    assert "Моро" in books[0].name

    pages = LTD_SPEC.extract_pages(soup, LTD_SPEC.base_url, client)
    assert len(pages) == 1
    assert pages[0].number == "2"

    solutions = client.get_solutions(pages[0])
    assert len(solutions) == 1
    assert "exercise/1/2.jpg" in solutions[0].image_src
