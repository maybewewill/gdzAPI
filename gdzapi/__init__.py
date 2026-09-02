"""Modern unified GDZ API library supporting 9 providers."""

from __future__ import annotations

from .client import AsyncClient, Client
from .exceptions import GDZError, NetworkError, NotFoundError, ParsingError
from .models import AwaitableList, Book, Class, Page, Solution, Subject
from .providers import Provider, ProviderSpec, PROVIDERS

# Provider Factory Aliases
GDZ = Client.gdz
AsyncGDZ = AsyncClient.gdz

Euroki = Client.euroki
AsyncEuroki = AsyncClient.euroki

MegaResheba = Client.megaresheba
AsyncMegaResheba = AsyncClient.megaresheba

GDZRaketa = Client.raketa
AsyncGDZRaketa = AsyncClient.raketa

Reshak = Client.reshak
AsyncReshak = AsyncClient.reshak

Pomogalka = Client.pomogalka
AsyncPomogalka = AsyncClient.pomogalka

Skysmart = Client.skysmart
AsyncSkysmart = AsyncClient.skysmart

GDZPutina = Client.putina
AsyncGDZPutina = AsyncClient.putina

GDZLTD = Client.ltd
AsyncGDZLTD = AsyncClient.ltd

__all__ = [
    # Core Engine
    "Client",
    "AsyncClient",
    "Provider",
    "ProviderSpec",
    "PROVIDERS",
    # Providers
    "GDZ",
    "AsyncGDZ",
    "Euroki",
    "AsyncEuroki",
    "MegaResheba",
    "AsyncMegaResheba",
    "GDZRaketa",
    "AsyncGDZRaketa",
    "Reshak",
    "AsyncReshak",
    "Pomogalka",
    "AsyncPomogalka",
    "Skysmart",
    "AsyncSkysmart",
    "GDZPutina",
    "AsyncGDZPutina",
    "GDZLTD",
    "AsyncGDZLTD",
    # Models
    "Class",
    "Subject",
    "Book",
    "Page",
    "Solution",
    "AwaitableList",
    # Exceptions
    "GDZError",
    "NetworkError",
    "ParsingError",
    "NotFoundError",
]
