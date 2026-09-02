"""Unit tests for HTTP client layer and exceptions."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest
import requests

from gdzapi.client import SyncHTTPClient, parse_soup
from gdzapi.exceptions import GDZError, NetworkError


def test_exceptions_hierarchy():
    err = NetworkError("Connection refused", url="https://example.com", status_code=503)
    assert isinstance(err, GDZError)
    assert err.url == "https://example.com"
    assert err.status_code == 503


def test_parse_soup_fallback():
    soup = parse_soup("<p>Hello</p>", parser="invalid_parser_name")
    assert soup.find("p").text == "Hello"


def test_client_network_error_wrapping():
    client = SyncHTTPClient("https://example.com")
    with patch.object(client.session, "get", side_effect=requests.ConnectionError("Failed")):
        with pytest.raises(NetworkError) as exc_info:
            client.get("/test")
        assert "HTTP request failed" in str(exc_info.value)
        assert exc_info.value.url == "https://example.com/test"
