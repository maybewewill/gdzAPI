"""Integration tests against live websites. Run with: pytest -m live"""

from __future__ import annotations

import pytest
from gdzapi import Client, AsyncClient


@pytest.mark.live
def test_live_gdz():
    client = Client.gdz(timeout=10)
    subjects = client.subjects
    assert len(subjects) > 0


@pytest.mark.live
def test_live_euroki():
    client = Client.euroki(timeout=10)
    subjects = client.subjects
    assert len(subjects) > 0


@pytest.mark.live
def test_live_megaresheba():
    client = Client.megaresheba(timeout=10)
    subjects = client.subjects
    assert len(subjects) > 0


@pytest.mark.live
def test_live_raketa():
    client = Client.raketa(timeout=10)
    classes = client.classes
    assert len(classes) == 11


@pytest.mark.live
def test_live_reshak():
    client = Client.reshak(timeout=10)
    subjects = client.subjects
    assert len(subjects) > 0


@pytest.mark.live
def test_live_pomogalka():
    client = Client.pomogalka(timeout=10)
    classes = client.classes
    assert len(classes) == 11


@pytest.mark.live
def test_live_skysmart():
    client = Client.skysmart(timeout=10)
    classes = client.classes
    assert len(classes) == 11


@pytest.mark.live
def test_live_putina():
    client = Client.putina(timeout=10)
    classes = client.classes
    assert len(classes) == 11


@pytest.mark.live
def test_live_ltd():
    client = Client.ltd(timeout=10)
    classes = client.classes
    assert len(classes) == 11


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_async_client():
    async with AsyncClient.reshak(timeout=10) as client:
        subjects = await client.get_subjects()
        assert len(subjects) > 0
