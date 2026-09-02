"""Unit tests for utility functions."""

from __future__ import annotations

from bs4 import BeautifulSoup as BS
from gdzapi.utils import clean_text, normalize_url, safe_text


def test_normalize_url():
    base = "https://www.gdz.ru"
    assert normalize_url(base, "//gdz.ru/img/1.jpg") == "https://gdz.ru/img/1.jpg"
    assert normalize_url(base, "/matematika/") == "https://www.gdz.ru/matematika/"
    assert normalize_url(base, "matematika/") == "https://www.gdz.ru/matematika/"
    assert normalize_url(base, "https://other.com/a.png") == "https://other.com/a.png"
    assert normalize_url(base, "") == ""


def test_clean_text():
    assert clean_text("  Привет,   мир! \n \t ") == "Привет, мир!"
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_safe_text():
    soup = BS("<div><p class='author'>Иванов И.И.</p></div>", "html.parser")
    assert safe_text(soup, ".author") == "Иванов И.И."
    assert safe_text(soup, ".missing", default="Н/Д") == "Н/Д"
    assert safe_text(None, default="None") == "None"
