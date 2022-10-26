"""Tests for `kronos` module."""
from typing import Generator

import pytest

import os
os.environ['KRONOS_DATERANGE'] = 'LATEST'

import pytz
from datetime import datetime, timedelta

import src.kronos as k
from src.kronos.kronos import ISO_FMT, Kronos, DEFAULT_TZ, DEFAULT_FORMAT

tz = pytz.timezone(DEFAULT_TZ)


@pytest.fixture
def version() -> Generator[str, None, None]:
    """Sample pytest fixture."""
    yield k.__version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == "0.0.4"


def test_day_range():
    end_date = datetime.now(tz=tz).strftime(DEFAULT_FORMAT)
    start_date = (datetime.now(tz=tz) - timedelta(days=5)).strftime(DEFAULT_FORMAT)

    kronos = Kronos(start_date, end_date)

    day_range = [x for x in kronos.day_range()]

    assert len(day_range) == 6


def test_set_start_time():
    kronos = Kronos()
    kronos.set_start_time(hour=8, minute=30, second=15)

    assert kronos.format_start('%H:%M:%S') == '08:30:15'

def test_set_end_time():
    kronos = Kronos()
    kronos.set_end_time(hour=8, minute=30, second=15)

    assert kronos.format_end('%H:%M:%S') == '08:30:15'

def test_start_timestamp():
    kronos = Kronos()
    assert type(kronos.start_ts) == float

def test_end_timestamp():
    kronos = Kronos()
    assert type(kronos.end_ts) == float


def test_set_start_time():
    kronos = Kronos()
    kronos.set_start_time(hour=12, minute=15, second=59)
    assert kronos.format_start(ISO_FMT).split(' ')[-1] == '12:15:59'


def test_set_end_time():
    kronos = Kronos()
    kronos.set_end_time(hour=12, minute=15, second=59)
    assert kronos.format_end(ISO_FMT).split(' ')[-1] == '12:15:59'
