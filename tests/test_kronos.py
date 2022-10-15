"""Tests for `kronos` module."""
from typing import Generator

import pytest

import pytz
from datetime import datetime, timedelta

import kronos as k
from src.kronos import Kronos, DEFAULT_TZ, DEFAULT_FORMAT, ISO_FMT

tz = pytz.timezone(DEFAULT_TZ)


@pytest.fixture
def version() -> Generator[str, None, None]:
    """Sample pytest fixture."""
    yield k.__version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == "0.0.1"


def test_day_range():
    end_date = datetime.now(tz=tz).strftime(DEFAULT_FORMAT)
    start_date = (datetime.now(tz=tz) - timedelta(days=5)).strftime(DEFAULT_FORMAT)

    kronos = Kronos(start_date, end_date)

    day_range = [x for x in kronos.day_range()]

    assert len(day_range) == 6
